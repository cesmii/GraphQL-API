using GraphQL;
using GraphQL.Client.Http;
using GraphQL.Client.Serializer.Newtonsoft;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http.Headers;
using System.Threading.Tasks;

/* Dependencies to install via NuGet:
 - GraphQL.Client v3.2 (Deinok,Alexander Rose,graphql-dotnet)
 - GraphQL.Client.Serializer.Newtonsoft v3.2 (Deinok,Alexander Rose,graphql-dotnet)
 - Newtonsoft.Json v12 (James Newton-King)
 - Microsoft.IdentityModel.Tokens v6.8 (Microsoft)
 - System.IdentityModel.Tokens.Jwt v6.8 (Microsoft) */

namespace CESMII.Samples
{
    class DotNetGraphQLRequestSample
    {
        //Your instance-specific information
        static readonly string instanceGraphQLEndpoint = "https://YOURINSTANCE.cesmii.net/graphql";

        /* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
            But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
            expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
            you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
        static string currentBearerToken = "Value from Instance Portal -- Do not include the word Bearer or the trailing spaces.";
        // eg: eyJyb2xlIjoieW91cl9yb2xlIiwiZXhwIjoxNDk5OTk5OTk5LCJ1c2VyX25hbWUiOiJ5b3VydXNlcm5hbWUiLCJhdXRoZW50aWNhdG9yIjoieW91cmF1dGgiLCJhdXRoZW50aWNhdGlvbl9pZCI6Ijk5IiwiaWF0Ijo5OTk5OTk5OTk5LCJhdWQiOiJhdWQiLCJpc3MiOiJpc3MifQ==

        /* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
            Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
            credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
            In the Authenticator setup, you will also configure role, and Token expiry. */
        static readonly string clientId = "YourAuthenticatorName";
        static readonly string clientSecret = "YourAuthenticatorPassword";
        static readonly string userName = "YourAuthenticatorBoundUserName";
        static readonly string role = "YourAuthenticatorRole";

        /// <summary>
        /// Forms and sends a GraphQL request (query or mutation) and returns the response
        /// </summary>
        /// <param name="content">The JSON payload you want to send to GraphQL</param>
        /// <param name="endPoint">The URL of the GraphQL endpoint</param>
        /// <param name="bearerToken">The Bearer Token granting authorization to use the endpoint</param>
        /// <returns>The JSON payload returned from the Server</returns>
        public static async Task<string> PerformGraphQLRequest(string content, string endPoint, string bearerToken)
        {
            var graphQLClient = new GraphQLHttpClient(endPoint, new NewtonsoftJsonSerializer());

            GraphQLRequest dataRequest = new GraphQLRequest() { Query = content };
            graphQLClient.HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearerToken);
            GraphQLResponse<JObject> dataResponse = await graphQLClient.SendQueryAsync<JObject>(dataRequest);
            JObject data = dataResponse.Data;
            return data.ToString(Formatting.Indented);
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
                  authenticationRequest(input: {{authenticator: ""{clientId}"", role: ""{role}"", userName: ""{userName}""}}) {{
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
                  authenticationValidation(input: {{authenticator: ""{clientId}"", signedChallenge: ""{challenge}|{clientSecret}""}}) {{
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

        // Main Program Method
        static async Task Main(string[] args)
        {
            Console.WriteLine("Requesting Data from CESMII Smart Manufacturing Platform...");
            Console.WriteLine();

            //Request some data -- this is an equipment query.
            //  Use Graphiql on your instance to experiment with additional queries
            //  Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries
            string smpQuery = $@"
                {{
                  equipments {{
                    id
                    displayName
                  }}
                }}";
            string smpResponse = "";

            try
            {
                //Try to request data with the current bearer token
                smpResponse = await PerformGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);
            }
            catch (Exception ex)
            {
                //An exception was thrown indicating the current bearer token is no longer allow.
                //  Authenticate and get a new token, then try again
                if (ex.Message.ToLower().IndexOf("forbidden") != -1 || ex.Message.ToLower().IndexOf("unauthorized") != -1)
                {
                    Console.WriteLine("Bearer Token expired!");
                    Console.WriteLine("Attempting to retreive a new GraphQL Bearer Token...");
                    Console.WriteLine();

                    //Authenticate
                    JwtSecurityToken newToken = await GetBearerToken(instanceGraphQLEndpoint);
                    currentBearerToken = newToken.RawData;

                    Console.WriteLine($"New Token received: {newToken.EncodedPayload}");
                    Console.WriteLine($"New Token valid until: {newToken.ValidTo.ToLocalTime()}");
                    Console.WriteLine();

                    //Re-try our data request, using the updated bearer token
                    //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
                    smpResponse = await PerformGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);
                }
                else
                {
                    Console.WriteLine("An error occured accessing the SM Platform!");
                    Console.WriteLine(ex.Message);
                    Environment.Exit(-1);
                }
            }

            Console.WriteLine("Response from SM Platform was...");
            Console.WriteLine(smpResponse);
            Console.WriteLine();
            Environment.Exit(0);
        }
    }
}
