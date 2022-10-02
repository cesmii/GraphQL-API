% Reference: https://www.mathworks.com/matlabcentral/fileexchange/80647-graphql-client.
% Reference: https://github.com/roslovets/MATLAB-GraphQL/

url = 'https://demo.cesmii.net/graphql';
% Fill the following information from the CESMII web https://demo.cesmii.net/developer/graphql-authenticator.
authenticator = '';
role = '';
password = '';
username = '';
% Get the Bearer token
token=get_token(url, authenticator, role, password, username);
opts=weboptions('HeaderFields',{'Authorization',[sprintf('Bearer %s', token)]})
% Compose your query
query = 'query { equipments { displayName, id }   }';
g = GraphQL(url, 'Query', query, 'WebOptions', opts);
res = g.execute();
res.data.equipments.displayName

function jwt = get_token(url, authenticator, role, password, username)
    % Create weboptions object (builtin in MATLAB) with specified header fields
    opts = weboptions('HeaderFields',{});
    % Optionally increase request timeout (usefull for heavy requests)
    opts.Timeout = 20;

    % Compose request query
    auth_request = 'mutation { authenticationRequest(input: {authenticator: "%s", role: "%s", userName: "%s"}) {jwtRequest {challenge message}}}';
    query_request = sprintf(auth_request, authenticator, role, username);
    % Create GraphQL object with predefined web options
    g = GraphQL(url, 'Query', query_request, 'WebOptions', opts);
    % Execute request query
    res = g.execute();
    challenge = res.data.authenticationRequest.jwtRequest.challenge;
    
    % Compose response query
    auth_validation = 'mutation { authenticationValidation(input: {authenticator: "%s", signedChallenge: "%s|%s"}) {jwtClaim}}';
    query_validation = sprintf(auth_validation, authenticator, challenge, password);
    % Create GraphQL object with predefined web options
    g = GraphQL(url, 'Query', query_validation, 'WebOptions', opts);
    % Execute response query
    res = g.execute();
    jwt = res.data.authenticationValidation.jwtClaim;
end
