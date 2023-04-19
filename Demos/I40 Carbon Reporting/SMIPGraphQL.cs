using GraphQL;
using GraphQL.Client.Http;
using GraphQL.Client.Serializer.Newtonsoft;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace SPSEventGridFunction
{
    static class SMIPGraphQL
    {
        //Your instance-specific information
        static string _endPoint = "https://demo.cesmii.net/graphql";
        static string _clientId = "";
        static string _clientSecret = "";
        static string _userName = "";
        static string _role = "";
        static string _currentBearerToken = "";
        static bool configSet = false;

        public static void SetConfig(string endpoint, string clientId, string clientSecret, string userName, string role, string currentBearerToken)
        {
            _endPoint = endpoint;
            _clientId = clientId;
            _clientSecret = clientSecret;
            _userName = userName;
            _role = role;
            _currentBearerToken = currentBearerToken;
            configSet = true;
        }

        /// <summary>
        /// Forms and sends a GraphQL request (query or mutation) and returns the response
        /// </summary>
        /// <param name="content">The JSON payload you want to send to GraphQL</param>
        /// <param name="endPoint">The URL of the GraphQL endpoint</param>
        /// <param name="bearerToken">The Bearer Token granting authorization to use the endpoint</param>
        /// <returns>The JSON payload returned from the Server</returns>
        public static async Task<string> PerformGraphQLRequest(string content, ILogger log)
        {
            if (configSet)
            {
                var graphQLClient = new GraphQLHttpClient(_endPoint, new NewtonsoftJsonSerializer());
                try
                {
                    GraphQLRequest dataRequest = new GraphQLRequest() { Query = content };
                    graphQLClient.HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _currentBearerToken);
                    GraphQLResponse<JObject> dataResponse = await graphQLClient.SendQueryAsync<JObject>(dataRequest);
                    JObject data = dataResponse.Data;
                    log.LogInformation("Mutation response: " + data.ToString());
                    return data.ToString(Formatting.Indented);
                }
                catch (Exception ex)
                {
                    //An exception was thrown indicating the current bearer token is no longer allow.
                    //  Authenticate and get a new token, then try again
                    if (ex.Message.ToLower().IndexOf("forbidden") != -1 || ex.Message.ToLower().IndexOf("unauthorized") != -1)
                    {
                        log.LogInformation("Bearer Token expired!");
                        log.LogInformation("Attempting to retreive a new GraphQL Bearer Token...");

                        //Authenticate
                        JwtSecurityToken newToken = await GetBearerToken(_endPoint);
                        _currentBearerToken = newToken.RawData;

                        log.LogInformation($"New Token received: {newToken.EncodedPayload}");
                        log.LogInformation($"New Token valid until: {newToken.ValidTo.ToLocalTime()}");

                        //Re-try our data request, using the updated bearer token
                        //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. We should do a better job.
                        return await PerformGraphQLRequest(content, log);
                    }
                    else
                    {
                        log.LogInformation("An error occured accessing the SM Platform!");
                        log.LogInformation(ex.Message);
                        return ex.Message;
                    }
                }
            }
            else
            {
                log.LogInformation("A SMIP GraphQL request was sent before configuration was set");
                return "Set configuration before sending GraphQL requests.";
            }
        }

        /// <summary>
        /// Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
        /// </summary>
        /// <param name="endPoint">The URL of the GraphQL endpoint</param>
        /// <returns>A valid JWT (or an exception if one can't be found! Add some error handling)</returns>
        public static async Task<JwtSecurityToken> GetBearerToken(string endPoint)
        {
            var graphQLClient = new GraphQLHttpClient(endPoint, new NewtonsoftJsonSerializer());

            // Step 1: Request a challenge
            string authRequestQuery = @$"
                mutation authRequest {{
                  authenticationRequest(input: {{authenticator: ""{_clientId}"", role: ""{_role}"", userName: ""{_userName}""}}) {{
                    jwtRequest {{
                      challenge
                      message
                    }}
                  }}
                }}";

            GraphQLRequest authRequest = new GraphQLRequest() { Query = authRequestQuery };
            GraphQLResponse<JObject> authResponse = await graphQLClient.SendQueryAsync<JObject>(authRequest);
            string challenge = authResponse.Data["authenticationRequest"]["jwtRequest"]["challenge"].Value<string>();
            Console.WriteLine($"Challenge received: {challenge}");

            // Step 2: Get token
            var authValidationQuery = @$"
                mutation authValidation {{
                  authenticationValidation(input: {{authenticator: ""{_clientId}"", signedChallenge: ""{challenge}|{_clientSecret}""}}) {{
                    jwtClaim
                  }}
                }}";

            GraphQLRequest validationRequest = new GraphQLRequest() { Query = authValidationQuery };
            GraphQLResponse<JObject> validationQLResponse = await graphQLClient.SendQueryAsync<JObject>(validationRequest);
            var tokenString = validationQLResponse.Data["authenticationValidation"]["jwtClaim"].Value<string>();
            var newJwtToken = new JwtSecurityToken(tokenString);
            return newJwtToken;

            //TODO: Handle errors!
        }

        
    }
}
