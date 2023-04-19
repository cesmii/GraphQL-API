using System;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using GraphQL;
using GraphQL.Client.Http;
using GraphQL.Client.Serializer.Newtonsoft;
using System.Collections.Generic;
using CESMII.EnergyConsumption.Functions.Models;
using System.Linq;
using System.Globalization;

namespace CESMII.EnergyConsumption.Functions
{
    /// <summary>
    /// Helper class to interact with ThinkIQ API
    /// </summary>
    public class SmipUtility 
    {
        private readonly string _GraphQLEndpoint;
        private readonly IConfigurationRoot _config;
        private readonly ILogger _log;

        /// <summary>
        /// Store and persist bearer token for life of this class.
        /// Code below will get new bearer token if this expired. 
        /// </summary>
        public string BearerToken { get; set; }

        public SmipUtility(IConfigurationRoot config, ILogger log)
        {
            _config = config;
            _log = log;
            _GraphQLEndpoint = config["SmipSettings:GraphQLEndpoint"];
        }

        /// <summary>
        /// Calls SMIP and gets a response of data. The query determines what data we are getting or posting.
        /// </summary>
        public async Task<String> GetSMIPresponse(string smpQuery)
        {
            //first time through this will be null so we need to get a new token
            if (string.IsNullOrEmpty(this.BearerToken))
            {
                this.BearerToken = await GetBearerTokenString();
            }
            //call method setup to handle token expired/re-issue scenario
            return await this.GetSMIPresponseInternal(smpQuery);
        }

        /// <summary>
        /// Calls SMIP and gets a response of data. The query determines what data we are getting or posting.
        /// </summary>
        private async Task<String> GetSMIPresponseInternal(string smpQuery, int counter = 1)
        {
            const string FUNCTION_NAME = "GetSMIPresponse";
            string response = "";

            //don't keep calling SMIP to authorize indefinitely, try a few times then inform user something is not configured properly
            if (counter > 5) throw new Exception("SMIP platform is not accepting our token. Check that you are authorized to use SMIP");

            try
            {
                //Try to request data with the current bearer token
                response = await PerformGraphQLRequest(smpQuery, _GraphQLEndpoint, BearerToken);
            }
            catch (Exception ex)
            {
                //TBD - we should only check for unauthorized?
                //An exception was thrown indicating the current bearer token is no longer allow.
                //  Authenticate and get a new token, then try again
                if (ex.Message.ToLower().IndexOf("forbidden") != -1 || ex.Message.ToLower().IndexOf("unauthorized") != -1)
                {
                    //we get into here if token is invalid/expired. Re-issue and then re-call this method.
                    //Counter - add in protection against infinite loop.
                    _log.LogWarning($"{FUNCTION_NAME}: Bearer Token expired. Getting new token from SMIP platform.");

                    this.BearerToken = await this.GetBearerTokenString();  //this will trigger retrieval of new bearer token

                    return await this.GetSMIPresponseInternal(smpQuery, counter++);
                }
                else
                {
                    _log.LogCritical(ex, $"{FUNCTION_NAME}: An error occured accessing the SMIP: {ex.Message}");
                    throw;
                }
            }
            _log.LogTrace($"{FUNCTION_NAME}: SMIP platform response:");
            _log.LogTrace(response);
            return response;
        }

        /// <summary>
        /// Forms and sends a GraphQL request (query or mutation) and returns the response
        /// </summary>
        /// <param name="content">The JSON payload you want to send to GraphQL</param>
        /// <param name="endPoint">The URL of the GraphQL endpoint</param>
        /// <param name="bearerToken">The Bearer Token granting authorization to use the endpoint</param>
        /// <returns>The JSON payload returned from the Server</returns>
        ///
        private async Task<string> PerformGraphQLRequest(string content, string endPoint, string bearerToken)
        {
            const string FUNCTION_NAME = "PerformGraphQLRequest";

            var graphQLClient = new GraphQLHttpClient(endPoint, new NewtonsoftJsonSerializer());
            //JwtSecurityToken newToken = await GetBearerToken(instanceGraphQLEndpoint);
            //currentBearerToken = newToken.RawData;
            GraphQLRequest dataRequest = new GraphQLRequest() { Query = content };

            //_log.LogInformation($"{FUNCTION_NAME}: Authorize Token...");
            graphQLClient.HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", BearerToken);

            _log.LogInformation($"{FUNCTION_NAME}: Sending query async...");
            GraphQLResponse<JObject> dataResponse = await graphQLClient.SendQueryAsync<JObject>(dataRequest);

            //_log.LogInformation($"{FUNCTION_NAME}: Evaluating response data...");
            JObject data = dataResponse.Data;

            _log.LogInformation($"{FUNCTION_NAME}: Returning response...");
            //Console.Write(data);
            return data.ToString(Formatting.Indented);
        }

        /// <summary>
        /// Gets all attributes ids for an equipment type
        /// </summary>
        public async Task<Dictionary<string, Dictionary<string, string>>> GetSmipAttributeIds(string equipment_type_Id, string parent_equipment_id, Dictionary<string, string> places)
        {
            string smpQuery = $@"
                {{
                    equipments(filter: {{typeId: {{equalTo: ""{equipment_type_Id}""}} }}) {{
                    id
                    displayName
                    description
                    attributes {{
                        displayName
                        id}}
                    }}
                }}";

            //Send the query to the platform and gets all the equipments info
            string response = await GetSMIPresponse(smpQuery);
            var res = JsonConvert.DeserializeObject<JObject>(response);
            var equipments = res["equipments"];
            var attribute_ids_info = new Dictionary<string, Dictionary<string, string>>();

            //parse the returned info into attribute_ids_info
            foreach (var equipment in equipments)
            {
                string current_name = equipment["description"].ToString();
                var attribute_ids = new Dictionary<string, string>();
                foreach (var atttribute in equipment["attributes"])
                {
                    string current_attr = atttribute["displayName"].ToString();
                    string current_val = atttribute["id"].ToString();
                    attribute_ids.Add(current_attr, current_val);
                }
                if (!attribute_ids_info.ContainsKey(current_name))
                    attribute_ids_info.Add(current_name, attribute_ids);
            }

            //check if all equipments exist, if not, create them and add the attribute ids to attribute_ids_info
            foreach (string place in places.Keys)
            {
                if (!attribute_ids_info.ContainsKey(places[place]))
                {
                    _log.LogInformation($"GetSmipAttributeIds: Creating missing equipment instance: {place} ({places[place]})");
                    try
                    {
                        string new_equip_info = await CreateEquipment(place, equipment_type_Id, parent_equipment_id, places[place]);
                        var new_equip_json = JsonConvert.DeserializeObject<JObject>(new_equip_info);
                        var new_equip = new_equip_json["createEquipment"]["equipment"];
                        string current_name = new_equip["description"].ToString();
                        var attribute_ids = new Dictionary<string, string>();
                        foreach (var atttribute in new_equip["attributes"])
                        {
                            string current_attr = atttribute["displayName"].ToString();
                            string current_val = atttribute["id"].ToString();
                            attribute_ids.Add(current_attr, current_val);
                        }
                        attribute_ids_info.Add(current_name, attribute_ids);
                    } 
                    catch (Exception ex)
                    {
                        var message = "GetSmipAttributeIds could not create missing equipment, check that the parent equipment id exists. Exception was: " + ex.Message;
                        throw (new Exception(message));
                    }
                }
            }

            return attribute_ids_info;
        }

        /// <summary>
        /// Creates an equipment using the input values
        /// </summary>
        public async Task<String> CreateEquipment(string name, string equip_id, string parent_equip_id, string description)
        {

            string mutation = @$"
            mutation create{{
                createEquipment(
                    input:{{
                        equipment:{{
                                displayName: ""{name}"",
                                description: ""{description}"",
                                typeId: ""{equip_id}"",
                                partOfId: ""{parent_equip_id}""

                        }}
                    }}
			    ){{
                    equipment {{
                        id
                        displayName
                        description
                        attributes {{
                            displayName
                            id
                        }}
                    }}
                }}
            }}";

            string response = await GetSMIPresponse(mutation);
            return response;
        }

        /// <summary>
        /// Format the response into one string that's used in mutation to send data to the smip platform
        /// </summary>
        /// <param name="format"></param>
        /// <param name="result"></param>
        /// <returns></returns>
        public static string FormatResponse(string format, JObject result)
        {
            //Console.WriteLine("Formatting SMIP items");
            string all_entries = "";
            if (result.GetValue("series").HasValues)
            {
                List<SmipDataItem> Data = result["series"][0]["data"]
                .Select(d => new SmipDataItem
                {
                    timestamp = DateTime.ParseExact((string)d[0], format,
                                    new CultureInfo("en-US"),
                                    DateTimeStyles.None).ToString("yyyy-MM-ddTHH:mm:ss'Z'"),
                    value = ((string)d[1]),
                    status = "1"
                })
                .ToList()
                ;

                List<String> FormatedData = Data
                        .Select(d => $@"{{timestamp: ""{d.timestamp}"", value: ""{d.value}"", status: ""1""}}")
                        .ToList();
                all_entries = "[" + string.Join(",", FormatedData) + "]";
            }
            else
            {
                Console.WriteLine("no data in jobject");
            }
            return all_entries;
        }

        public static string FormatItem(SmipDataItem item)
        {
            //Console.WriteLine("Formatting SmipDataItem");
            string timestamp = DateTime.Parse(item.timestamp).ToString("yyyy-MM-ddTHH:mm:ss'Z'");
            string formattedItem = "{timestamp:\"" + timestamp + "\", value:\"" + item.value + "\", status:\"1\"}";
            return formattedItem;
        }

        /// <summary>
        /// Form one big query to update multiple attributes at the same time
        /// </summary>
        /// <param name="entry_list"></param>
        /// <param name="attribute_id_list"></param>
        /// <returns></returns>
        public static string FormGroupedQueries(List<string> entry_list, List<string> attribute_id_list)
        {
            var len = entry_list.Count;
            string temp_mutation = @$"mutation insertdata{{";
            for (int i = 0; i < len; i++)
            {
                temp_mutation += "t" + @$"{i}: " + @$"replaceTimeSeriesRange(
                    input: {{
                    attributeOrTagId: ""{attribute_id_list[i]}"", 
                    entries:{entry_list[i]},
                    }}
                  ) {{
                    clientMutationId
                    json
                  }}";
            }
            temp_mutation += @$"}}";
            return temp_mutation;
        }

        private async Task<string> GetBearerTokenString()
        {
            const string FUNCTION_NAME = "GetBearerTokenString";
            _log.LogInformation($"{FUNCTION_NAME}...");

            //Authenticate
            JwtSecurityToken newToken = await GetBearerToken(
                _config["SmipSettings:ClientId"],
                _config["SmipSettings:ClientSecret"],
                _config["SmipSettings:Role"],
                _config["SmipSettings:UserName"],
                _GraphQLEndpoint);

            //TBD - come back to this with log.LogInformation
            _log.LogTrace($"{FUNCTION_NAME}: New Token: {newToken.EncodedPayload}");
            _log.LogTrace($"{FUNCTION_NAME}: New Token valid until: {newToken.ValidTo.ToLocalTime()}");

            return newToken.RawData;
        }

        /// <summary>
        /// Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
        /// </summary>
        /// <param name="endPoint">The URL of the GraphQL endpoint</param>
        /// <returns>A valid JWT (or an exception if one can't be found! Add some error handling)</returns>
        private async Task<JwtSecurityToken> GetBearerToken(string clientId, string clientSecret, string role, string userName, string endPoint)
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


    }
}
