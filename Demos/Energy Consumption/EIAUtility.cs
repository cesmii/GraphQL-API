using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Linq;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Configuration;
using System.Text;
using System.Diagnostics;

namespace CESMII.EnergyConsumption.Functions
{
    /// <summary>
    /// Helper class
    /// </summary>
    public class EIAUtility 
    {
        private readonly IConfigurationRoot _config;
        private readonly ILogger _log;
        private readonly SmipUtility _smipUtility;
        static string HourlyInputTimeFormat = "yyyyMMdd'T'HH'Z'";
        static string StateInputTimeFormat = "yyyy";

        public EIAUtility(IConfigurationRoot config, ILogger log)
        {
            _config = config;
            _log = log;
            _smipUtility = new SmipUtility(config, log);
        }

        #region Processing Methods

        /// <summary>
        /// Process small regions energy demand data
        /// </summary>
        public async Task<StringBuilder> ProcessSmallRegionData(StringBuilder sbResponse, string functionName, Stopwatch sw)
        {
            LogAppSettingsInfo();
            string FUNCTION_NAME = functionName;
            var msg = "";

            msg = $"{FUNCTION_NAME}: Go get small region energy demand data...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            //TODO: Move to separate JSON file and load / bind to .NET object using JsonConvert
            var places_abbr = SmallRegionAbbreviations;
            var input_time_format = HourlyInputTimeFormat;
            var series_ids = RegionSeriesIds;
            var suffixes = SmallRegionSuffixes;
            var type_id = _config["SmipSettings:SmallRegionEquipmentTypeId"];
            var parent_id = _config["SmipSettings:ParentEquipmentId"];

            //TODO: move to appSettings
            Dictionary<string, Dictionary<string, string>> attribute_ids = await _smipUtility.GetSmipAttributeIds(type_id, parent_id, places_abbr);

            msg = $"{FUNCTION_NAME}: Getting energy consumption data by small regions...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            string response = await GetAndProcessEIAData(places_abbr, series_ids, attribute_ids, suffixes, GetTimeRange(), input_time_format);

            //show whether it worked
            msg = $"{FUNCTION_NAME}: SMIP Response:";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            _log.LogInformation(response);
            sbResponse.AppendLine(response);

            //show finished message
            msg = $"{FUNCTION_NAME}: Getting energy consumption data by small regions: completed.";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            return sbResponse;
        }

        /// <summary>
        /// Process big regions energy demand and generation by sources data
        /// </summary>
        public async Task<StringBuilder> ProcessBigRegionData(StringBuilder sbResponse, string functionName, Stopwatch sw)
        {
            LogAppSettingsInfo();
            string FUNCTION_NAME = functionName;
            var msg = "";

            msg = $"{FUNCTION_NAME}: Go get big region energy demand and generation by sources data...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            var time_range = GetTimeRange();

            //TODO: Move to separate JSON file and load / bind to .NET object using JsonConvert
            var places_abbr = BigRegionAbbreviations;
            var input_time_format = HourlyInputTimeFormat;
            var series_ids = RegionSeriesIds;
            var suffixes = BigRegionSuffixes;
            var type_id = _config["SmipSettings:BigRegionEquipmentTypeId"];
            var parent_id = _config["SmipSettings:ParentEquipmentId"];

            //TODO: move to appSettings
            Dictionary<string, Dictionary<string, string>> attribute_ids = await _smipUtility.GetSmipAttributeIds(type_id, parent_id, places_abbr);

            msg = $"{FUNCTION_NAME}: Getting energy demand and energy generation by sources data of big regions...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            string response = await GetAndProcessEIAData(places_abbr, series_ids, attribute_ids, suffixes, time_range, input_time_format);

            //show whether it worked
            msg = $"{FUNCTION_NAME}: SMIP Response:";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            _log.LogInformation(response);
            sbResponse.AppendLine(response);

            //show finished message
            msg = $"{FUNCTION_NAME}: Getting energy demand and energy generation by sources data of big regions: completed.";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            return sbResponse;
        }

        /// <summary>
        /// Process states energy demand and generation data
        /// </summary>
        public async Task<StringBuilder> ProcessStateData(StringBuilder sbResponse, string functionName, Stopwatch sw)
        {
            LogAppSettingsInfo();
            string FUNCTION_NAME = functionName;
            var msg = "";

            msg = $"{FUNCTION_NAME}: Go get state energy production and consumption..";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            string yesterday = DateTime.UtcNow.AddYears(-10).ToString("yyyyMMdd");
            string today = DateTime.UtcNow.ToString("yyyyMMdd");
            string time_range = "&start=" + yesterday + "&end=" + today;

            //TODO: Move to separate JSON file and load / bind to .NET object using JsonConvert
            var places_abbr = StateAbbreviations;
            var input_time_format = StateInputTimeFormat;
            var series_ids = StateSeriesIds;
            var suffixes = StateSuffixes;
            var type_id = _config["SmipSettings:StateEquipmentTypeId"];
            var parent_id = _config["SmipSettings:ParentEquipmentId"];

            Dictionary<string, Dictionary<string, string>> attribute_ids = await _smipUtility.GetSmipAttributeIds(type_id, parent_id, places_abbr);

            msg = $"{FUNCTION_NAME}: Getting energy production and consumption of states...";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            string response = await GetAndProcessEIAData(places_abbr, series_ids, attribute_ids, suffixes, time_range, input_time_format);

            //show whether it worked
            msg = $"{FUNCTION_NAME}: SMIP Response:";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);
            _log.LogInformation(response);
            sbResponse.AppendLine(response);

            //show finished message
            msg = $"{FUNCTION_NAME}: Getting energy production and consumption of states: completed.";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            return sbResponse;
        }

        /// <summary>
        /// Process the energy consumption and production data of total 48 states
        /// </summary>
        public async Task<StringBuilder> ProcessCountryData(StringBuilder sbResponse, string functionName, Stopwatch sw)
        {
            LogAppSettingsInfo();
            string FUNCTION_NAME = functionName;
            var msg = "";

            msg = $"{FUNCTION_NAME}: Go get total country energy production and consumption..";
            _log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            var time_range = GetTimeRange();

            //TODO: Move to separate JSON file and load / bind to .NET object using JsonConvert
            var places_abbr = CountryAbbreviations;
            var input_time_format = HourlyInputTimeFormat;
            var series_ids = CountrySeriesIds;
            var suffixes = CountrySuffixes;
            var type_id = _config["SmipSettings:StateEquipmentTypeId"];
            var parent_id = _config["SmipSettings:ParentEquipmentId"];
            Dictionary<string, Dictionary<string, string>> attribute_ids = await _smipUtility.GetSmipAttributeIds(type_id, parent_id, places_abbr);

            string response = await GetAndProcessEIAData(places_abbr, series_ids, attribute_ids, suffixes, time_range, input_time_format);

            //show whether it worked
            msg = $"{FUNCTION_NAME}: SMIP Response:";
            _log.LogTrace(msg);
            sbResponse.AppendLine(msg);
            _log.LogTrace(response);
            sbResponse.AppendLine(response);

            return sbResponse;
        }

        /// <summary>
        /// This function gets the values of each attribute of each equipment from DOE, and update those values to the SMIP platform
        /// </summary>
        public async Task<String> GetAndProcessEIAData(Dictionary<string, string> places, Dictionary<string, string> series_ids, Dictionary<string, Dictionary<string, string>> attribute_ids, Dictionary<string, string> suffixes, string time_range, string input_time_format)
        {
            string FUNCTION_NAME = "GetAndProcessEIAData";

            var response = "";
            var url = _config["DoeSettings:Url"];
            var apiKey = _config["DoeSettings:ApiKey"];
            foreach (var place in places)
            {
                string place_name = place.Key;
                string place_abbr = place.Value;
                List<String> attr_id_list = new List<string>();
                List<string> entry_data_list = new List<string>();

                _log.LogInformation($"{FUNCTION_NAME}: Working on Region: {place_name} ({place_abbr})");

                // for each attribute, get data from DOE api
                foreach (var attribute_name in attribute_ids[place_abbr].Keys)
                {
                    string series_id = "";
                    if (series_ids.ContainsKey(attribute_name))
                    {
                        series_id = series_ids[attribute_name];//for states, attribute "production" and attribute "consumption" use different series id
                    }
                    else
                    {
                        series_id = series_ids["all"];//for big_regions and small_regions and country, this means all attributes for the equipment share the same series id
                    }
                    string attribute_suffix = suffixes[attribute_name];
                    string attribute_id = attribute_ids[place_abbr][attribute_name];
                    //modify this so we can log the params being sent prior to call. Don't log API key
                    string parameters = "series_id=" + series_id + place_abbr + attribute_suffix + time_range;
                    //string parameters = $"?api_key={api_key}&&series_id=" + series_id + place_abbr + attribute_suffix + time_range;
                    string entry_data = await EIAUtility.GetFormattedEIAresponse(_log, url, apiKey, parameters, input_time_format);
                    if (entry_data != "")
                    {
                        _log.LogTrace($"{FUNCTION_NAME}: EIA Response - {entry_data}");
                        attr_id_list.Add(attribute_id);
                        entry_data_list.Add(entry_data);
                    }
                    else
                    {
                        _log.LogWarning($"{FUNCTION_NAME}: EIA Response - none");
                    }
                }

                //only call SMIP if we have data to send
                if (entry_data_list == null || entry_data_list.Count == 0)
                {
                    _log.LogInformation($"{FUNCTION_NAME}: Nothing to send to SMIP for place Name: {place_name}, place abbr: {place_abbr}.");
                }
                else
                {
                    var new_query = SmipUtility.FormGroupedQueries(entry_data_list, attr_id_list);//form one big mutation string
                    _log.LogInformation($"{FUNCTION_NAME}: Calling GetSMIPresponse. Query: {new_query}");
                    response += await _smipUtility.GetSMIPresponse(new_query);//update data to the platform
                }
            }

            return response;
        }

        #endregion

        #region Helper Methods

        /// <summary>
        /// Gets the time range for the process data functions
        /// </summary>
        /// <returns></returns>
        public string GetTimeRange()
        {
            //TODO: move some settings to appSettings (ie days offset).
            //TODO: or let the user pass in dateoffset as query string
            var offsetDaysStart = int.Parse(_config["DoeSettings:DaysOffsetStart"]);
            var offsetDaysEnd = int.Parse(_config["DoeSettings:DaysOffsetEnd"]);
            string dtStart = DateTime.UtcNow.AddDays(offsetDaysStart).ToString("yyyyMMdd");
            string dtEnd = DateTime.UtcNow.AddDays(offsetDaysEnd).ToString("yyyyMMdd");
            return $"&start={dtStart}&end={dtEnd}";
        }

        /// <summary>
        /// Helper method to show what settings are being used. 
        /// </summary>
        /// <returns></returns>
        public void LogAppSettingsInfo()
        {
            _log.LogInformation($"SmipSettings:GraphQLEndpoint== {_config["SmipSettings:GraphQLEndpoint"]}");
            _log.LogInformation($"SmipSettings:ParentEquipmentId== {_config["SmipSettings:ParentEquipmentId"]}");
            _log.LogInformation($"SmipSettings:BigRegionEquipmentTypeId== {_config["SmipSettings:BigRegionEquipmentTypeId"]}");
            _log.LogInformation($"SmipSettings:SmallRegionEquipmentTypeId== {_config["SmipSettings:SmallRegionEquipmentTypeId"]}");
            _log.LogInformation($"SmipSettings:StateEquipmentTypeId== {_config["SmipSettings:StateEquipmentTypeId"]}");
        }

        /// <summary>
        /// Gets the energy data for one attribute from DOE api then format it into one string
        /// </summary>
        public static async Task<String> GetFormattedEIAresponse(ILogger log, string url, string apiKey, string parameters, string input_time_format)
        {
            string FUNCTION_NAME = "GetFormattedEIAresponse";
            log.LogInformation($"{FUNCTION_NAME}: Url: {url}");
            log.LogInformation($"{FUNCTION_NAME}: Request Parameters: {parameters}");

            HttpClient client = new HttpClient();
            client.BaseAddress = new Uri(url);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            HttpResponseMessage response = await client.GetAsync($"?api_key={apiKey}&&{parameters}").ConfigureAwait(false);
            string all_entries = "";
            if (response.IsSuccessStatusCode)
            {
                var jsonString = await response.Content.ReadAsStringAsync();

                //add some protective code. If the DOE cannot find the file, it returns 
                //an HTML page in the indicating file not found.
                if (jsonString.IndexOf("<!DOCTYPE html") >= 0 && jsonString.ToLower().IndexOf("file not found") >= 0)
                {
                    log.LogCritical($"{FUNCTION_NAME}: File not found for parameters: {parameters}.");
                    log.LogTrace($"{FUNCTION_NAME}: Response:");
                    log.LogTrace(jsonString);
                    return "";
                }

                try
                {
                    var res = JsonConvert.DeserializeObject<JObject>(jsonString);
                    if (res["series"]?.Any() != true)
                    {
                        log.LogWarning($"{FUNCTION_NAME}: Data not found: {parameters}.");
                        log.LogWarning($"{FUNCTION_NAME}: Response: {jsonString}.");
                    }
                    else
                    {
                        all_entries = SmipUtility.FormatResponse(input_time_format, res);
                    }
                }
                catch (JsonSerializationException ex)
                {
                    //log specific stuff around this exception
                    log.LogCritical($"{FUNCTION_NAME}: Could not deserialize response: {ex.Message}.");
                    log.LogCritical($"{FUNCTION_NAME}: Response: {jsonString}.");
                    
                    //TBD - should we let program proceed under this scenario?
                    //Let the program continue onto the next item in this scenario. 
                    //Don't stop the whole process because of one bad item.
                    //bubble up to top level so we get full stack trace
                    //throw; 
                }
            }
            return all_entries;
        }

        #endregion

        #region Dictionaries
        static Dictionary<string, string> RegionSeriesIds = new Dictionary<string, string>()
            {
                {"all", "EBA." }
            };
        static Dictionary<string, string> SmallRegionSuffixes = new Dictionary<string, string>()
            {
                {"demand", ".D.H" }
            };
        static Dictionary<string, string> BigRegionSuffixes = new Dictionary<string, string>()
            {
                {"generation_total", "-ALL.D.H" },
                {"demand", "-ALL.NG.H" },
                {"generation_coal", "-ALL.NG.COL.H" },
                {"generation_natural_gas", "-ALL.NG.NG.H" },
                {"generation_hydro", "-ALL.NG.WAT.H" },
                {"generation_nuclear", "-ALL.NG.NUC.H" },
                {"generation_petroleum", "-ALL.NG.OIL.H" },
                {"generation_solar", "-ALL.NG.SUN.H" },
                {"generation_wind", "-ALL.NG.WND.H" },
                {"generation_other", "-ALL.NG.OTH.H" }
            };
        static Dictionary<string, string> StateSeriesIds = new Dictionary<string, string>()
            {
                {"production", "SEDS.TEPRB." },
                {"consumption", "SEDS.TETCB." }
            };
        static Dictionary<string, string> StateSuffixes = new Dictionary<string, string>()
            {
                {"production", ".A" },
                {"consumption", ".A" }
            };
        static Dictionary<string, string> SmallRegionAbbreviations
        {
            get
            {
                return new Dictionary<string, string>(){
                {"smallregion_CISO_San Diego Gas and Electric", "CISO-SDGE"},
                {"smallregion_CISO_Southern California Edison", "CISO-SCE"},
                {"smallregion_CISO_Valley Electric Association", "CISO-VEA"},
                {"smallregion_ERCO_Coast", "ERCO-COAS"},
                {"smallregion_ERCO_East", "ERCO-EAST"},
                {"smallregion_ERCO_Far West", "ERCO-FWES"},
                {"smallregion_ERCO_North Central", "ERCO-NCEN"},
                {"smallregion_ERCO_North", "ERCO-NRTH"},
                {"smallregion_ERCO_South Central", "ERCO-SCEN"},
                {"smallregion_ERCO_South", "ERCO-SOUT"},
                {"smallregion_ERCO_West", "ERCO-WEST"},
                {"smallregion_ISNE_Connecticut", "ISNE-4004"},
                {"smallregion_ISNE_Maine", "ISNE-4001"},
                {"smallregion_ISNE_New Hampshire", "ISNE-4002"},
                {"smallregion_ISNE_Northeast Mass.", "ISNE-4008"},
                {"smallregion_ISNE_Rhode Island", "ISNE-4005"},
                {"smallregion_ISNE_Southeast Mass.", "ISNE-4006"},
                {"smallregion_ISNE_Vermont", "ISNE-4003"},
                {"smallregion_ISNE_Western-Central Mass.", "ISNE-4007"},
                {"smallregion_MISO_Zone 1", "MISO-0001"},
                {"smallregion_MISO_Zone 4", "MISO-0004"},
                {"smallregion_MISO_Zone 6", "MISO-0006"},
                {"smallregion_MISO_Zones 2 and 7", "MISO-0027"},
                {"smallregion_MISO_Zones 3 and 5", "MISO-0035"},
                {"smallregion_MISO_Zones 8, 9, and 10", "MISO-8910"},
                {"smallregion_NYIS_Capital", "NYIS-ZONF"},
                {"smallregion_NYIS_Central", "NYIS-ZONC"},
                {"smallregion_NYIS_Dunwoodie", "NYIS-ZONI"},
                {"smallregion_NYIS_Genesee", "NYIS-ZONB"},
                {"smallregion_NYIS_Hudson Valley", "NYIS-ZONG"},
                {"smallregion_NYIS_Long Island", "NYIS-ZONK"},
                {"smallregion_NYIS_Millwood", "NYIS-ZONH"},
                {"smallregion_NYIS_Mohawk Valley", "NYIS-ZONE"},
                {"smallregion_NYIS_New York City", "NYIS-ZONJ"},
                {"smallregion_NYIS_North", "NYIS-ZOND"},
                {"smallregion_NYIS_West", "NYIS-ZONA"},
                {"smallregion_PJM_Allegheny Power zone", "PJM-AP"},
                {"smallregion_PJM_American Electric Power zone", "PJM-AEP"},
                {"smallregion_PJM_American Transmission Systems, Inc. zone", "PJM-ATSI"},
                {"smallregion_PJM_Atlantic Electric zone", "PJM-AE"},
                {"smallregion_PJM_Baltimore Gas & Electric zone", "PJM-BC"},
                {"smallregion_PJM_Commonwealth Edison zone", "PJM-CE"},
                {"smallregion_PJM_Dayton Power & Light zone", "PJM-DAY"},
                {"smallregion_PJM_Delmarva Power & Light zone", "PJM-DPL"},
                {"smallregion_PJM_Dominion Virginia Power zone", "PJM-DOM"},
                {"smallregion_PJM_Duke Energy Ohio/Kentucky zone", "PJM-DEOK"},
                {"smallregion_PJM_Duquesne Lighting Company zone", "PJM-DUQ"},
                {"smallregion_PJM_East Kentucky Power Cooperative zone", "PJM-EKPC"},
                {"smallregion_PJM_Jersey Central Power & Light zone", "PJM-JC"},
                {"smallregion_PJM_Metropolitan Edison zone", "PJM-ME"},
                {"smallregion_PJM_PECO Energy zone", "PJM-PE"},
                {"smallregion_PJM_Pennsylvania Electric zone", "PJM-PN"},
                {"smallregion_PJM_Pennsylvania Power & Light zone", "PJM-PL"},
                {"smallregion_PJM_Potomac Electric Power zone", "PJM-PEP"},
                {"smallregion_PJM_Public Service Electric & Gas zone", "PJM-PS"},
                {"smallregion_PJM_Rockland Electric (East) zone", "PJM-RECO"},
                {"smallregion_PNM_Kirtland Air Force Base", "PNM-KAFB"},
                {"smallregion_PNM_Kit Carson Electric Cooperative", "PNM-KCEC"},
                {"smallregion_PNM_Los Alamos County", "PNM-LAC"},
                {"smallregion_PNM_Navajo Tribal Utility Authority", "PNM-NTUA"},
                {"smallregion_PNM_PNM System Firm Load", "PNM-PNM"},
                {"smallregion_PNM_Tri-State Generation and Transmission", "PNM-TSGT"},
                {"smallregion_SWPP_AEPW American Electric Power West", "SWPP-CSWS"},
                {"smallregion_SWPP_City of Springfield", "SWPP-SPRM"},
                {"smallregion_SWPP_Empire District Electric Company", "SWPP-EDE"},
                {"smallregion_SWPP_Grand River Dam Authority", "SWPP-GRDA"},
                {"smallregion_SWPP_Independence Power & Light", "SWPP-INDN"},
                {"smallregion_SWPP_KCP&L Greater Missouri Operations", "SWPP-MPS"},
                {"smallregion_SWPP_Kansas City Board of Public Utilities", "SWPP-KACY"},
                {"smallregion_SWPP_Kansas City Power & Light", "SWPP-KCPL"},
                {"smallregion_SWPP_Lincoln Electric System", "SWPP-LES"},
                {"smallregion_SWPP_Nebraska Public Power District", "SWPP-NPPD"},
                {"smallregion_SWPP_Oklahoma Gas and Electric Co.", "SWPP-OKGE"},
                {"smallregion_SWPP_Omaha Public Power District", "SWPP-OPPD"},
                {"smallregion_SWPP_Southwestern Public Service Company", "SWPP-SPS"},
                {"smallregion_SWPP_Sunflower Electric", "SWPP-SECI"},
                {"smallregion_SWPP_Westar Energy", "SWPP-WR"},
                {"smallregion_SWPP_Western Area Power Upper Great Plains East", "SWPP-WAUE"},
                {"smallregion_SWPP_Western Farmers Electric Cooperative", "SWPP-WFEC"}
            };
            }
        }
        static Dictionary<string, string> BigRegionAbbreviations
        {
            get
            {
                return new Dictionary<string, string>(){

                {"bigregion_California", "CAL"},
                {"bigregion_Carolinas", "CAR"},
                {"bigregion_Central", "CENT"},
                {"bigregion_Florida", "FLA"},
                {"bigregion_Mid_Atlantic", "MIDA"},
                {"bigregion_Midwest", "MIDW"},
                {"bigregion_New England", "NE"},
                {"bigregion_New York", "NY"},
                {"bigregion_Northwest", "NW"},
                {"bigregion_Southeast", "SE"},
                {"bigregion_Southwest", "SW"},
                {"bigregion_Tennessee", "TEN"},
                {"bigregion_Texas", "TEX"}
            };
            }
        }
        static Dictionary<string, string> StateAbbreviations
        {
            get
            {
                return new Dictionary<string, string>(){

                {"state_AL","AL" },
                {"state_AR","AR" },
                {"state_AZ","AZ" },
                {"state_CA","CA" },
                {"state_CO","CO" },
                {"state_CT","CT" },
                {"state_DC","DC" },
                {"state_DE","DE" },
                {"state_FL","FL" },
                {"state_GA","GA" },
                {"state_HI","HI" },
                {"state_IA","IA" },
                {"state_ID","ID" },
                {"state_IL","IL" },
                {"state_IN","IN" },
                {"state_KS","KS" },
                {"state_KY","KY" },
                {"state_LA","LA" },
                {"state_MA","MA" },
                {"state_MD","MD" },
                {"state_ME","ME" },
                {"state_MI","MI" },
                {"state_MN","MN" },
                {"state_MO","MO" },
                {"state_MS","MS" },
                {"state_MT","MT" },
                {"state_NC","NC" },
                {"state_ND","ND" },
                {"state_NE","NE" },
                {"state_NH","NH" },
                {"state_NJ","NJ" },
                {"state_NM","NM" },
                {"state_NV","NV" },
                {"state_NY","NY" },
                {"state_OH","OH" },
                {"state_OK","OK" },
                {"state_OR","OR" },
                {"state_PA","PA" },
                {"state_RI","RI" },
                {"state_SC","SC" },
                {"state_SD","SD" },
                {"state_TN","TN" },
                {"state_TX","TX" },
                {"state_UT","UT" },
                {"state_VA","VA" },
                {"state_VT","VT" },
                {"state_WA","WA" },
                {"state_WI","WI" },
                {"state_WV","WV" },
                {"state_WY","WY" },
            };
            }
        }
        static Dictionary<string, string> CountryAbbreviations
        {
            get
            {
                return new Dictionary<string, string>(){

                {"us_energy","US48"}
                };

            }
        }
        static Dictionary<string, string> CountrySeriesIds = new Dictionary<string, string>()
        {
            {"all", "EBA." },
        };
        static Dictionary<string, string> CountrySuffixes = new Dictionary<string, string>()
        {
            {"production", "-ALL.NG.H" },
            {"consumption", "-ALL.D.H" }
        };
        #endregion

    }
}
