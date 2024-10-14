/* 
Requires: ES5.1+ and HTTPS (most browsers since 2011)
*/
var instanceGraphQLEndpoint = "https://YOURINSTANCE.cesmii.net/graphql";

/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "Value from Instance Portal -- You must include the prefix Bearer followed by a space";
// eg: Bearer eyJyb2xlIjoieW91cl9yb2xlIiwiZXhwIjoxNDk5OTk5OTk5LCJ1c2VyX25hbWUiOiJ5b3VydXNlcm5hbWUiLCJhdXRoZW50aWNhdG9yIjoieW91cmF1dGgiLCJhdXRoZW50aWNhdGlvbl9pZCI6Ijk5IiwiaWF0Ijo5OTk5OTk5OTk5LCJhdWQiOiJhdWQiLCJpc3MiOiJpc3MifQ==

/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */
var clientId = "YourAuthenticatorName";
var clientSecret = "YourAuthenticatorPassword";
var userName = "YourAuthenticatorBoundUserName";
var role = "YourAuthenticatorRole";

//Forms and sends a GraphQL request (query or mutation) and returns the response
function performGraphQLRequest(query, endPoint, bearerToken, callBack) {
  var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", endPoint);
    xmlhttp.setRequestHeader('Content-Type', 'application/json');
    if (bearerToken)
      xmlhttp.setRequestHeader('Authorization', bearerToken);
    xmlhttp.send(query);
    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState == XMLHttpRequest.DONE) {
        if (callBack)
          callBack(xmlhttp.responseText);
      }
    };
    //TODO: Handle errors!
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
function getBearerToken(callBack) {

    // Step 1: Request a challenge
    performGraphQLRequest(JSON.stringify({
        "query": " mutation {\
            authenticationRequest(input: \
              {authenticator:\"" + clientId + "\", \
              role: \"" + role + "\", \
              userName: \"" + userName + "\"})\
             { jwtRequest { challenge, message } } }"
      }), instanceGraphQLEndpoint, null, function(responseText) {
        var authResponse = JSON.parse(responseText);
        var challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
        document.body.innerHTML += "<p>Challenge received: " + challenge + "</p>";
    
        // Step 2: Get token
        performGraphQLRequest(JSON.stringify({
            "query": " mutation {\
                authenticationValidation(input: \
                  {authenticator:\"" + clientId + "\", \
                  signedChallenge: \"" + challenge + "|" + clientSecret + "\"})\
                 { jwtClaim } }"
        }), instanceGraphQLEndpoint, null, function(responseText) {
          var challengeResponse = JSON.parse(responseText);
          newJwtToken = challengeResponse.data.authenticationValidation.jwtClaim;
          callBack(newJwtToken);
        }.bind(this));
      }.bind(this));
    //TODO: Handle errors!
}
  
//Main Program Function
function doMain() {
    document.body.innerHTML += "<p>Requesting Data from CESMII Smart Manufacturing Platform...</p>";

    /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
    var smpQuery = JSON.stringify({
        "query": " query {\
          equipments {\
            id\
            displayName\
          }\
        }",
      });
    smpResponse = performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken, function(responseText) {
      var smpResponse = JSON.parse(responseText);
      if (JSON.stringify(smpResponse).indexOf("expired") != -1)
      {
          document.body.innerHTML += "<p>Bearer Token expired!</p>";
          document.body.innerHTML += "<p>Attempting to retreive a new GraphQL Bearer Token...</p>";
  
          //Authenticate
          getBearerToken(function(newTokenResponse) {
            currentBearerToken = "Bearer " + newTokenResponse;
  
            document.body.innerHTML += "<p>New Token received: " + JSON.stringify(newTokenResponse) + "</p>";
    
            //Re-try our data request, using the updated bearer token
            //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
            performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken, function(responseText) {
                var smpResponse = JSON.parse(responseText);
                showResult(smpResponse);
            }.bind(this));
          }.bind(this));
      } else {
        showResult(smpResponse)
      }
    }.bind(this));
}

function showResult(smpResponse) {
  document.body.innerHTML += "<p>Response from SM Platform was... </p>";
  document.body.innerHTML += "<pre>" + JSON.stringify(smpResponse, null, 2).replace(/(?:\r\n|\r|\n)/g, '<br>').replace(/\s+/g, '&nbsp;') + "</pre>";
}