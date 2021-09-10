
/* Dependenices to install via npm
 - node-fetch
 Tested with Node.JS 12.6.3
*/
const fetch = require('node-fetch');
const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";
var tanks = [1319, 1325, 1283, 1290, 1296, 1302, 1308];
/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZGVtb19yb19ncm91cCIsImV4cCI6MTYyNzQwMjAxOSwidXNlcl9uYW1lIjoid2VuamllIiwiYXV0aGVudGljYXRvciI6IkRlbW8gQ0VTTUlJIiwiYXV0aGVudGljYXRpb25faWQiOiIxMjQ2IiwiaWF0IjoxNjI3NDAwMjE5LCJhdWQiOiJwb3N0Z3JhcGhpbGUiLCJpc3MiOiJwb3N0Z3JhcGhpbGUifQ.Rg8i_jbIz9g2UHB1eAWfl6EIslBB3yfgLzK43KH6bM8";
// eg: Bearer eyJyb2xlIjoieW91cl9yb2xlIiwiZXhwIjoxNDk5OTk5OTk5LCJ1c2VyX25hbWUiOiJ5b3VydXNlcm5hbWUiLCJhdXRoZW50aWNhdG9yIjoieW91cmF1dGgiLCJhdXRoZW50aWNhdGlvbl9pZCI6Ijk5IiwiaWF0Ijo5OTk5OTk5OTk5LCJhdWQiOiJhdWQiLCJpc3MiOiJpc3MifQ==

/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */
const clientId = "YourAuthenticatorName";
const clientSecret = "YourAuthenticatorPassword";
const userName = "YourAuthenticatorBoundUserName";
const role = "YourAuthenticatorRole";

//Call main program function
//doMain();

//Forms and sends a GraphQL request (query or mutation) and returns the response
async function performGraphQLRequest(query, endPoint, bearerToken) {
    console.log("using gphql.....")
    var opt = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: query
      }
    if (bearerToken && bearerToken != "")
        opt.headers.Authorization = bearerToken;
    const response = await fetch(endPoint, opt);
    return await response.json();

    //TODO: Handle errors!
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
async function getBearerToken() {

    // Step 1: Request a challenge
    var authResponse = await performGraphQLRequest(JSON.stringify({
        "query": " mutation {\
            authenticationRequest(input: \
              {authenticator:\"" + clientId + "\", \
              role: \"" + role + "\", \
              userName: \"" + userName + "\"})\
             { jwtRequest { challenge, message } } }"
      }), instanceGraphQLEndpoint);
    var challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
    console.log("Challenge received: " + challenge);

    // Step 2: Get token
    var challengeResponse = await performGraphQLRequest(JSON.stringify({
        "query": " mutation {\
            authenticationValidation(input: \
              {authenticator:\"" + clientId + "\", \
              signedChallenge: \"" + challenge + "|" + clientSecret + "\"})\
             { jwtClaim } }"
    }), instanceGraphQLEndpoint);

    var newJwtToken = challengeResponse.data.authenticationValidation.jwtClaim;
    return newJwtToken;

    //TODO: Handle errors!
}
  
//Main Program Function
async function doMain(tank) {
    console.log("Requesting Data from CESMII Smart Manufacturing Platform...")
    console.log();

    /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
    var smpQuery = JSON.stringify({
        query: `{
          getRawHistoryDataWithSampling(
            maxSamples: 1
            ids: ["1283"]
            startTime: "2021-07-15 00:00:00+00"
            endTime: "2021-07-21 00:12:00+00"
          ) {
            id
            floatvalue
            dataType
            ts
            status
          }
        }`,
      });
    smpResponse = await performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);

    if (JSON.stringify(smpResponse).indexOf("expired") != -1)
    {
        console.log("Bearer Token expired!");
        console.log("Attempting to retreive a new GraphQL Bearer Token...");
        console.log();

        //Authenticate
        var newTokenResponse = await getBearerToken(instanceGraphQLEndpoint);
        currentBearerToken = "Bearer " + newTokenResponse;

        console.log("New Token received: " + JSON.stringify(newTokenResponse));
        console.log();

        //Re-try our data request, using the updated bearer token
        //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
        smpResponse = await performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);
    }

    

    console.log("Response from SM Platform was... ");
    console.log(JSON.stringify(smpResponse, null, 2));
    console.log();
    return parseFloat(smpResponse.data.getRawHistoryDataWithSampling[1].floatvalue);
}
