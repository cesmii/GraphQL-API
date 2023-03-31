smip = {};

smip.currentBearerToken = "";

smip.performGraphQLRequest = async function performGraphQLRequest(query, endPoint, bearerToken) {
    return new Promise(
        function (resolve, reject) {
            let xhr = new XMLHttpRequest();
            xhr.responseType = "json";
            xhr.open("POST", endPoint);
            xhr.setRequestHeader("Content-Type", "application/json");
            if (bearerToken && bearerToken != "")
                xhr.setRequestHeader("Authorization", bearerToken)
            xhr.onload = function() {
                if (xhr.status == 200)
                    resolve (xhr.response);
                else
                    reject (xhr.status);
            };
            xhr.send(JSON.stringify(query));
        }
    );
}

smip.getBearerToken = async function getBearerToken() {
    return new Promise(
        async function (resolve, reject) {
            // Step 1: Request a challenge
            var theQuery = {
                query: `mutation { authenticationRequest(input:
                    {authenticator: "${config.authenticator}", 
                    role: "${config.role}", 
                    userName: "${config.name}"})
                    { jwtRequest { challenge, message } } 
                }`
            };
            var authResponse = await smip.performGraphQLRequest(theQuery, config.url);
            var challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
            //console.log("Challenge received: " + challenge);

            // Step 2: Get token
            var theQuery = {
                query: `mutation { authenticationValidation(input:
                    {authenticator:"${config.authenticator}", 
                    signedChallenge: "${challenge}|${config.password}"})
                    { jwtClaim } 
                }`
            };
            var challengeResponse = await smip.performGraphQLRequest(theQuery, config.url);
            //console.log(challengeResponse)
            var newJwtToken = "Bearer " + challengeResponse.data.authenticationValidation.jwtClaim;
            console.log("Token received: " + newJwtToken);
            resolve(newJwtToken);

            //TODO: Handle errors!
        }
    );
}
