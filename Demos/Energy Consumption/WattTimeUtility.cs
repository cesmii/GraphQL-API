using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Net.Http;
using System.Net.Http.Headers;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using CESMII.EnergyConsumption.Functions.Models;
using Microsoft.Extensions.Configuration;
using System.Text;
using System.Diagnostics;
using System.Linq;

namespace CESMII.EnergyConsumption.Functions
{
    /// <summary>
    /// Helper class
    /// </summary>
    public class WattTimeUtility
    {
        private readonly IConfigurationRoot _config;
        private readonly ILogger _log;
        private readonly SmipUtility _smipUtility;

        public WattTimeUtility(IConfigurationRoot config, ILogger log)
        {
            _config = config;
            _log = log;
            _smipUtility = new SmipUtility(config, log);
        }

        #region Processing Methods

        /// <summary>
        /// Process the carbon impact data provided by WattTime
        /// </summary>
        public async Task<StringBuilder> ProcessWattTimeData(StringBuilder sbResponse, string functionName, Stopwatch sw)
        {
            LogAppSettingsInfo();
            string FUNCTION_NAME = functionName;
            var msg = "";

            msg = $"{FUNCTION_NAME}: Go get Watt-Time data..";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            var time_range = GetTimeRange();

            string response = await GetAndProcessWattTimeData(time_range);

            //show whether it worked
            msg = $"{FUNCTION_NAME}: SMIP Response:";
            _log.LogTrace(msg);
            sbResponse.AppendLine(msg);
            _log.LogTrace(response);
            sbResponse.AppendLine(response);

            return sbResponse;
        }

        /// <summary>
        /// Method to call Watt-Time API and process results into SMIP
        /// </summary>
        private async Task<String> GetAndProcessWattTimeData(string time_range)
        {
            string FUNCTION_NAME = "GetAndProcessWattTimeData";

            var apiBaseUrl = _config["WattTimeSettings:Url"];
            var apiUser = _config["WattTimeSettings:UserName"];
            var apiPass = _config["WattTimeSettings:Password"];

            string msg;
            Stopwatch sw = new Stopwatch();
            sw.Start();
            StringBuilder sbResponse = new StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Starting at {DateTime.Now}";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            
            //Trade username and password for a token
            msg = $"{FUNCTION_NAME}: Authorizing with WattTime...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            string apiToken = await GetWTAuthToken(apiBaseUrl, apiUser, apiPass);

            //  Get list of regions from WattTime
            JArray regionList = await GetWTRegions(apiBaseUrl, apiToken);
            Dictionary<string, string> places = new Dictionary<string, string>();
            msg = $"{FUNCTION_NAME}: Found {regionList.Count} regions...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            foreach (var region in regionList)
            {
                var key = "carbonregion_" + region["name"].ToString();  //Form region name
                var val = region["ba"].ToString();  //Put region code in description (unfortunate, but consistent with EIA approach)
                places.Add(key, val);
            }

            // Get region attribute IDs from SMIP
            //  Creating regions in SMIP if needed
            msg = $"{FUNCTION_NAME}: Syncing SMIP regions...\n";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            var attributes = await _smipUtility.GetSmipAttributeIds(_config["SmipSettings:CarbonRegionEquipmentTypeId"], _config["SmipSettings:ParentEquipmentId"], places);

            // For each region:
            foreach (var region in regionList)
            {
                msg = $"{FUNCTION_NAME}: Parsing data for region: " + region["ba"].ToString();
                _log.LogInformation(msg);
                sbResponse.AppendLine(msg);

                // Get data
                var watttime_data = await GetWTDataForRegion(apiBaseUrl, apiToken, region["ba"].ToString(), GetTimeRange());
                // Update SMIP
                string response = await ProcessWTDataForRegion(region["ba"].ToString(), watttime_data, attributes);
            }

            msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            return sbResponse.ToString();
        }

        #endregion

        #region Helper Methods

        private async Task<string> GetWTAuthToken(string urlbase, string username, string password)
        {
            HttpClient httpClient = new HttpClient();
            var contentType = new MediaTypeWithQualityHeaderValue("application/json");
            httpClient.DefaultRequestHeaders.Accept.Add(contentType);
            // Assign the authentication headers
            var authToken = Encoding.ASCII.GetBytes($"{username}:{password}");
            httpClient.DefaultRequestHeaders.Authorization = new
            AuthenticationHeaderValue("Basic",Convert.ToBase64String(authToken));
            // Call Login on WattTime api
            HttpResponseMessage response = await httpClient.GetAsync(urlbase + "/login");
            if (response.IsSuccessStatusCode)
            {
                var stringData = await response.Content.ReadAsStringAsync();
                var result = (JObject)JsonConvert.DeserializeObject<object>(stringData);
                var token = result.SelectToken("token").ToString();
                return token;
            } 
            else
            {
                throw new Exception(response.StatusCode + " - WattTime login failed");
            }
        }

        private async Task<JArray> GetWTRegions(string urlbase, string token)
        {

            HttpClient httpClient = new HttpClient();
            var contentType = new MediaTypeWithQualityHeaderValue("application/json");
            httpClient.DefaultRequestHeaders.Accept.Add(contentType);
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            HttpResponseMessage response = await httpClient.GetAsync(urlbase + "/ba-access");
            if (response.IsSuccessStatusCode)
            {
                var stringData = await response.Content.ReadAsStringAsync();
                return (JArray)JsonConvert.DeserializeObject<object>(stringData);
            }
            else
            {
                throw new Exception(response.StatusCode + " - WattTime region list request failed");
            }
        }

        private async Task<WattTimeDataPoint[]> GetWTDataForRegion(string urlbase, string token, string regionCode, string timeRange)
        {
            var FUNCTION_NAME = "GetWTDataForRegion";
            HttpClient httpClient = new HttpClient();
            var contentType = new MediaTypeWithQualityHeaderValue("application/json");
            httpClient.DefaultRequestHeaders.Accept.Add(contentType);
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            var queryUrl = urlbase + "data?ba=" + regionCode + timeRange;
            HttpResponseMessage response = await httpClient.GetAsync(queryUrl);
            if (response.IsSuccessStatusCode)
            {
                try
                {
                    var stringData = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<WattTimeDataPoint[]>(stringData);
                }
                catch (Exception ex)
                {
                    _log.LogWarning($"{FUNCTION_NAME}: WattTime response could not be parsed - " + ex.Message);
                    return null;
                }
            }
            else
            {
                throw new Exception($"{FUNCTION_NAME}: {response.StatusCode} - WattTime data request failed");
            }
        }

        private async Task<string> ProcessWTDataForRegion(string regionCode, WattTimeDataPoint[] watttime_data, Dictionary<string, Dictionary<string, string>> attributes)
        {
            var FUNCTION_NAME = "ProcessWTDataForRegion";
            var response = "";
            List<string> attr_id_list = new List<string>();
            List<string> entry_data_list = new List<string>();
            List<string> smipDataItems = new List<string>();

            _log.LogInformation($"{FUNCTION_NAME}: Updating Region: {regionCode}");

            //Only value matters for WattTime
            attr_id_list.Add(attributes[regionCode]["value"]);
            foreach (var entry in watttime_data)
            {
                _log.LogInformation($"Updating data: {entry.point_time} value {entry.value}");
                // for each attribute, get data from DOE api
                var smipData = new SmipDataItem();
                smipData.timestamp = entry.point_time.ToString();
                smipData.value = entry.value.ToString();
                smipData.status = "1";
                smipDataItems.Add(SmipUtility.FormatItem(smipData));
            }
            entry_data_list.Add("[" + string.Join(",",smipDataItems.ToArray<string>()) + "]");
            //JsonConvert.SerializeObject();
            //only call SMIP if we have data to send
            if (entry_data_list == null || entry_data_list.Count == 0)
            {
                _log.LogInformation($"{FUNCTION_NAME}: Nothing to send to SMIP for place Name: {regionCode}.");
            }
            else
            {
                //TODO: SMIP doesn't like our query because the values aren't coming in as an array
                var new_query = SmipUtility.FormGroupedQueries(entry_data_list, attr_id_list);//form one big mutation string
                _log.LogInformation($"{FUNCTION_NAME}: Calling GetSMIPresponse. Query: {new_query}");
                response += await _smipUtility.GetSMIPresponse(new_query);//update data to the platform   
            }
            return response;
        }

        /// <summary>
        /// Gets the time range for the process data functions
        /// </summary>
        /// <returns>A string formatted time range for the last hour of data</returns>
        public string GetTimeRange()
        {
            string dtStart = DateTime.UtcNow.AddHours(-1).ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss");
            string dtEnd = DateTime.UtcNow.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss");
            return $"&starttime={dtStart}&endtime={dtEnd}";
        }

        /// <summary>
        /// Helper method to show what settings are being used. 
        /// </summary>
        /// <returns></returns>
        public void LogAppSettingsInfo()
        {
            _log.LogInformation($"WattTimeSettings:UserName== {_config["WattTimeSettings:UserName"]}");
            //_log.LogInformation($"WattTimeSettings:Password== {_config["WattTimeSettings:Password"]}");
            _log.LogInformation($"WattTimeSettings:Url== {_config["WattTimeSettings:Url"]}");
            _log.LogInformation($"SmipSettings:GraphQLEndpoint== {_config["SmipSettings:GraphQLEndpoint"]}");
            _log.LogInformation($"SmipSettings:ParentEquipmentId== {_config["SmipSettings:ParentEquipmentId"]}");
            _log.LogInformation($"SmipSettings:CarbonRegionEquipmentTypeId== {_config["SmipSettings:CarbonRegionEquipmentTypeId"]}");
        }

        #endregion

    }
}
