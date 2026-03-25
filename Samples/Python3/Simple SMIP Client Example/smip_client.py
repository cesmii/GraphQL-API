import json
import time
import base64
from pathlib import Path
import requests


class SMIPClient:
    """Simple SMIP client that reads config.json and can get/refresh a JWT.

    Expects a local, gitignored `config.json` with structure matching
    `config.example.json` in the workspace root.
    """

    def __init__(self, config_path=None):
        cfg_path = Path(config_path) if config_path else Path(__file__).with_name('config.json')
        if not cfg_path.exists():
            raise FileNotFoundError(f"Config file not found: {cfg_path}")
        cfg = json.loads(cfg_path.read_text())
        smip = cfg.get('SMIP', {})
        self.endpoint = smip.get('graphQlEndpoint')
        self.client_id = smip.get('clientId')
        self.client_secret = smip.get('clientSecret')
        self.role = smip.get('role')
        self.user_name = smip.get('userName')

        missing = [k for k, v in (
            ('graphQlEndpoint', self.endpoint),
            ('clientId', self.client_id),
            ('clientSecret', self.client_secret),
            ('role', self.role),
            ('userName', self.user_name),
        ) if v is None]
        if missing:
            raise ValueError('Missing keys in config.json: ' + ', '.join(missing))

        self._jwt = None
        # refresh margin (seconds) before expiry to proactively refresh
        self._refresh_margin = 60

    def _decode_jwt_payload(self, token: str):
        """Return the decoded JWT payload as a dict, or None on failure.

        Accepts either the bare token or a header value like 'Bearer <token>'.
        """
        if not token:
            return None
        if token.startswith('Bearer '):
            token = token.split(' ', 1)[1]
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # Add padding if necessary and use urlsafe_b64decode
        padding = '=' * (-len(payload_b64) % 4)
        try:
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            return json.loads(payload_bytes)
        except Exception:
            return None

    def _token_expiry(self, token: str):
        """Return expiry `exp` as int unix timestamp, or None."""
        payload = self._decode_jwt_payload(token)
        if not payload:
            return None
        return payload.get('exp')

    def _post(self, payload, headers=None):
        headers = headers or {}
        r = requests.post(self.endpoint, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

    def _authenticate(self):
        # Step 1: request a challenge
        auth_request = f"mutation authRequest {{ authenticationRequest(input: {{authenticator: \"{self.client_id}\", role: \"{self.role}\", userName: \"{self.user_name}\"}}) {{ jwtRequest {{ challenge, message }} }} }}"
        resp = self.query(auth_request, op_type='mutation', add_auth=False)
        jwt_request = resp.get('data', {}).get('authenticationRequest', {}).get('jwtRequest')
        if not jwt_request:
            raise RuntimeError('authenticationRequest returned unexpected payload: ' + json.dumps(resp))
        challenge = jwt_request.get('challenge')
        if not challenge:
            raise RuntimeError('Authentication challenge not provided: ' + jwt_request.get('message', ''))

        # Step 2: send back signed challenge
        signed = f"{challenge}|{self.client_secret}"
        auth_validation = f"mutation authValidation {{ authenticationValidation(input: {{authenticator: \"{self.client_id}\", signedChallenge: \"{signed}\"}}) {{ jwtClaim }} }}"
        resp = self.query(auth_validation, op_type='mutation', add_auth=False)
        jwt_claim = resp.get('data', {}).get('authenticationValidation', {}).get('jwtClaim')
        if not jwt_claim:
            raise RuntimeError('authenticationValidation failed: ' + json.dumps(resp))
        self._jwt = f"Bearer {jwt_claim}"
        return self._jwt

    def get_jwt(self, force_refresh=False):
        # If explicitly forced or no token yet, authenticate
        if force_refresh or not self._jwt:
            return self._authenticate()

        # Otherwise check expiry and refresh proactively if close to expiry
        exp = self._token_expiry(self._jwt)
        if exp is None:
            # Can't parse expiry — be conservative and return current token
            return self._jwt

        now = int(time.time())
        if now >= exp - self._refresh_margin:
            return self._authenticate()

        return self._jwt

    def query(self, query: str, variables: dict = None, headers: dict = None, op_type: str = 'query', add_auth: bool = True):
        """Execute a GraphQL `query` or `mutation` and return the parsed JSON response.

        Parameters
        - query: GraphQL string
        - variables: optional variables dict
        - headers: optional headers dict; `Authorization` will be added if missing
        - op_type: either 'query' or 'mutation' (defaults to 'query')
        """
        if op_type not in ('query', 'mutation'):
            raise ValueError("op_type must be 'query' or 'mutation'")

        headers = dict(headers or {})
        if add_auth and 'Authorization' not in headers:
            headers['Authorization'] = self.get_jwt()

        # GraphQL servers expect the operation string in the 'query' field
        payload = {'query': query}
        if variables is not None:
            payload['variables'] = variables
        return self._post(payload, headers=headers)

    def get_equipment(self):
        # replaced by get_libraries for quick test purposes
        return self.get_libraries()

    def get_libraries(self):
        """Test method returning `libraries { id displayName }`"""
        query = '{ libraries { id displayName } }'
        return self.query(query)


__all__ = ['SMIPClient']
