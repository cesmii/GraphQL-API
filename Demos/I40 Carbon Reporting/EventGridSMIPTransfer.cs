// Default URL for triggering event grid function in the local environment.
// http://localhost:7071/runtime/webhooks/EventGrid?functionName={functionname}
using System;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.EventGrid.Models;
using Microsoft.Azure.WebJobs.Extensions.EventGrid;
using Microsoft.Extensions.Logging;
using System.Net;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace SPSEventGridFunction
{
    /// <summary>
    /// This depends on a number of environment variables that are set in one of two ways:
    /// If you're running locally, configure in local.settings.json (see local.settings-example.json for a template)
    /// If running in Azure, configure in the Azure Function Configuration in the Azure Portal:
    ///     https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings
    ///  
    /// Also and very important, please see the dataMap at the bottom of this class. Its job is to provide the SMIP IDs for the attributes to be updated.
    /// </summary>
    public static class EventGridSMIPTransfer
    {

        [FunctionName("FestoTelemetryTrigger")]
        public static void Run([EventGridTrigger]EventGridEvent eventGridEvent, ILogger log)
        {
            log.LogInformation(eventGridEvent.Data.ToString());
            SMIPGraphQL.SetConfig(Environment.GetEnvironmentVariable("SMIPEndpoint"), Environment.GetEnvironmentVariable("SMIPClientId"), Environment.GetEnvironmentVariable("SMIPClientSecret"), Environment.GetEnvironmentVariable("SMIPUserName"), Environment.GetEnvironmentVariable("SMIPRole"), Environment.GetEnvironmentVariable("SMIPBearerToken"));

            int seconds = DateTime.Now.Second;
            int throttleRate;
            if (!int.TryParse(Environment.GetEnvironmentVariable("ThrottleRate"), out throttleRate))
                throttleRate = 5;

            if (seconds % throttleRate == 0)
            {
                Dictionary<string, int> dataMap = loadTranslationMap();

                string useTimeStamp = makeUTCTimeStamp();
                string newPostData = "GraphQL Mutations are...\r\n";
                dynamic eventGridDataObj = JsonConvert.DeserializeObject(eventGridEvent.Data.ToString());
                var decodedFieldData = base64Decode(eventGridDataObj.body.ToString());
                string mutation;
                dynamic fieldDataObj = JsonConvert.DeserializeObject(decodedFieldData);
                foreach (var item in fieldDataObj.fields)
                {
                    //TODO: There are better ways to parse these JSON members... but none of them worked
                    string[] jsonParts = item.ToString().Split(":");
                    string key = jsonParts[0].Replace("\"", "");
                    string valueStr = jsonParts[1];
                    float valueFloat;
                    if (float.TryParse(valueStr, out valueFloat))   //Make sure we have a good value
                    {
                        if (dataMap.ContainsKey(key))   //Make sure we have a data map reference
                        {
                            mutation = makeSMIPMutation(dataMap[key], valueFloat, useTimeStamp);
                            newPostData += mutation;
                            log.LogInformation("Attemping mutation: " + mutation);
                            SMIPGraphQL.PerformGraphQLRequest(mutation, log);   //TODO: This is an async call so we're firing blind
                        }
                        else
                        {
                            log.LogInformation("Not building mutation for " + key + " because it couldn't be found in SMIP data map");
                        }
                    }
                    else
                    {
                        log.LogInformation("Not building mutation for " + key + " because value couldn't be parsed to float");
                    }

                }
                newPostData += "\r\n";
                postToTestSink(newPostData, log);
                postToTestSink(Environment.GetEnvironmentVariable("SMIPinstanceGraphQLEndpoint"), log);
            } 
            else
            {
                log.LogInformation("Skipping this update because of throttle rate (every " + throttleRate.ToString() + " seconds) and this was " + seconds.ToString() + " seconds.");
            }
            
        }

        private static void postToTestSink(string postData, ILogger log)
        {
            if (Environment.GetEnvironmentVariable("SendToTestSink") != "")
            {
                //POST to my server
                log.LogInformation("Posting mutations to test sink...");

                string url = Environment.GetEnvironmentVariable("SendToTestSink");
                var request = (HttpWebRequest)WebRequest.Create(url);
                var data = Encoding.ASCII.GetBytes(postData);

                request.Method = "POST";
                request.ContentType = "application/x-www-form-urlencoded";
                request.ContentLength = data.Length;

                using (var stream = request.GetRequestStream())
                {
                    stream.Write(data, 0, data.Length);
                }

                var response = (HttpWebResponse)request.GetResponse();
            }
        }

        private static string base64Decode(string base64EncodedData)
        {
            var base64EncodedBytes = System.Convert.FromBase64String(base64EncodedData);
            return System.Text.Encoding.UTF8.GetString(base64EncodedBytes);
        }

        private static string makeSMIPMutation(int id, float value, string timestamp)
        {
            string mutation = $@"
                mutation updateRequest {{
                  replaceTimeSeriesRange(input: {{attributeOrTagId: ""{id}"", entries: [{{timestamp: ""{timestamp}"", value: ""{value}"", status: ""1""}}]}})
                  {{  
                    json
                  }}
                }}";
            return mutation;
        }

        private static string makeUTCTimeStamp()
        {
            return DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.ffZ");
        }

        private static Dictionary<string, int> loadTranslationMap()
        {
            //TODO: This should come from a config file, or better yet...a Part 2 SMProfile!
            Dictionary<string, int> dataMap = new Dictionary<string, int>();
            dataMap.Add("VoltageL1", 37877);
            dataMap.Add("CurrentL1", 37876);
            dataMap.Add("ActivePowerL1", 37875);
            dataMap.Add("ApparentPowerL1", 37874);
            dataMap.Add("ReactivePowerL1", 37873);
            dataMap.Add("VoltageL2", 37883);
            dataMap.Add("CurrentL2", 37882);
            dataMap.Add("ActivePowerL2", 37881);
            dataMap.Add("ApparentPowerL2", 37880);
            dataMap.Add("ReactivePowerL2", 37879);
            dataMap.Add("VoltageL3", 37889);
            dataMap.Add("CurrentL3", 37888);
            dataMap.Add("ActivePowerL3", 37887);
            dataMap.Add("ApparentPowerL3", 37886);
            dataMap.Add("ReactivePowerL3", 37885);
            dataMap.Add("Flow1", 37891);
            dataMap.Add("Pressure1", 37892);
            dataMap.Add("Flow2", 37894);
            dataMap.Add("Pressure2", 37895);
            dataMap.Add("Flow3", 21159);
            dataMap.Add("Pressure3", 37898);
            dataMap.Add("Frequency", 37897);
            dataMap.Add("ActivePowerTotal", 37870);
            dataMap.Add("ApparentPowerTotal", 37869);
            dataMap.Add("ReactivePowerTotal", 37867);
            dataMap.Add("ActiveEnergy", 37871);
            return dataMap;
        }
    }
}
