using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using CESMII.EnergyConsumption.Functions.Config;

namespace CESMII.EnergyConsumption.Functions
{
    public static class EnergyConsumptionFunctions
    {

        #region Small Region Functions 

        /// <summary>
        /// Timer based trigger for common small region function
        /// Kick off hourly.
        /// 0 30 1 * * * == 1.30am every day
        /// 0 10 * * * * == 10 minutes past every hour of the day
        /// </summary>
        /// <remarks>Reference on timer expression: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-csharp#ncrontab-expressions</remarks>
        [FunctionName("ProcessSmallRegionDataTimer")]
        public static async Task FnTimerProcessSmallRegionData([TimerTrigger("0 10 * * * *", RunOnStartup = false)] TimerInfo myTimer, ILogger log, ExecutionContext context)
        {
            log.LogInformation("Timer based trigger fired for ProcessSmallRegionData");
            await ProcessSmallRegionData(log, context, "timer");
        }

        /// <summary>
        /// HTTP based trigger for common small region function
        /// </summary>
        /// <returns>Summary of actions as a string for logging</returns>
        [FunctionName("ProcessSmallRegionData")]
        public static async Task<IActionResult> FnProcessSmallRegionData(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = null)] HttpRequest req, ILogger log, ExecutionContext context)
        {
            log.LogInformation("HTTP based trigger fired for ProcessSmallRegionData");
            var result = await ProcessSmallRegionData(log, context, "http");
            return new OkObjectResult(result);
        }

        /// <summary>
        /// Common function to Process Small Region Data regardless of trigger
        /// </summary>
        public static async Task<string> ProcessSmallRegionData(ILogger log, ExecutionContext context, string triggerType)
        {
            const string FUNCTION_NAME = "ProcessSmallRegionData";
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
            var msg = "";
            sw.Start();

            System.Text.StringBuilder sbResponse = new System.Text.StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Started via {triggerType} at: {DateTime.Now}";
            log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            try
            {
                //get config data from appSettings.json
                msg = $"{FUNCTION_NAME}: Getting config data...";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);
                IConfigurationRoot config = ConfigUtil.GetConfig(context);

                msg = $"{FUNCTION_NAME}: Updating: {config["SmipSettings:GraphQLEndpoint"]}";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);

                //do the work
                var processor = new EIAUtility(config, log);
                sbResponse = await processor.ProcessSmallRegionData(sbResponse, FUNCTION_NAME, sw);
            }
            catch (Exception ex)
            {
                msg = $"{FUNCTION_NAME}: An exception occurred: {ex.Message}";
                log.LogCritical(ex, msg);
                sbResponse.AppendLine(msg);
            }
            finally
            {
                msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
                log.LogInformation(msg);
                sbResponse.AppendLine(msg);
            }

            //show the user how the data was processed.  
            return sbResponse.ToString();
        }

        #endregion

        #region Big Region Functions 

        /// <summary>
        /// Timer based trigger for common big region function
        /// Kick off hourly.
        /// 0 35 1 * * * == 1.30am every day
        /// 0 5 * * * * == 5 minutes past every hour of the day
        /// 0 */5 * * * * == 12 times an hour - at second 0 of every 5th minute of every hour of each day
        /// </summary>
        /// <remarks>Reference on timer expression: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-csharp#ncrontab-expressions</remarks>
        [FunctionName("ProcessBigRegionDataTimer")]
        public static async Task FnTimerProcessBigRegionData([TimerTrigger("0 */10 * * * *", RunOnStartup = false)] TimerInfo myTimer, ILogger log, ExecutionContext context)
        {
            log.LogInformation("Timer based trigger fired for ProcessBigRegionData");
            await ProcessBigRegionData(log, context, "timer");
        }

        /// <summary>
        /// HTTP based trigger for common big region function
        /// </summary>
        /// <returns>Summary of actions as a string for logging</returns>
        [FunctionName("ProcessBigRegionData")]
        public static async Task<IActionResult> FnProcessBigRegionData([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = null)] HttpRequest req, ILogger log, ExecutionContext context)
        {
            log.LogInformation("HTTP based trigger fired for ProcessBigRegionData");
            return await ProcessBigRegionData(log, context, "http");
        }
        
        /// <summary>
        /// Common function to Process Small Region Data regardless of trigger
        /// </summary>
        public static async Task<IActionResult> ProcessBigRegionData(ILogger log, ExecutionContext context, string triggerType)
        {
            const string FUNCTION_NAME = "ProcessBigRegionData";
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
            var msg = "";
            sw.Start();

            System.Text.StringBuilder sbResponse = new System.Text.StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Started via {triggerType} at: {DateTime.Now}";
            log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            try
            {
                //get config data from appSettings.json
                msg = $"{FUNCTION_NAME}: Getting config data...";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);
                IConfigurationRoot config = ConfigUtil.GetConfig(context);

                msg = $"{FUNCTION_NAME}: Updating: {config["SmipSettings:GraphQLEndpoint"]}";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);

                //do the work
                var processor = new EIAUtility(config, log);
                sbResponse = await processor.ProcessBigRegionData(sbResponse, FUNCTION_NAME, sw);
            }
            catch (Exception ex)
            {
                msg = $"{FUNCTION_NAME}: An exception occurred: {ex.Message}";
                log.LogCritical(ex, msg);
                sbResponse.AppendLine(msg);
            }
            finally
            {
                msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
                log.LogInformation(msg);
                sbResponse.AppendLine(msg);
            }

            //show the user how the data was processed.  
            return new OkObjectResult(sbResponse.ToString());
        }
        #endregion

        #region State Data Functions
        /// <summary>
        /// Timer based trigger for common state data function
        /// Kick off daily.
        /// 0 30 1 * * * == 1.30am every day
        /// </summary>
        /// <remarks>Reference on timer expression: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-csharp#ncrontab-expressions</remarks>
        [FunctionName("ProcessStateDataTimer")]
        public static async Task FnTimerProcessStateData([TimerTrigger("0 30 1 * * *", RunOnStartup = false)] TimerInfo myTimer, ILogger log, ExecutionContext context)
        {
            log.LogInformation("Timer based trigger fired for ProcessStateData");
            await ProcessStateData(log, context, "timer");
        }

        /// <summary>
        /// HTTP based trigger for common state data function
        /// </summary>
        /// <returns>Summary of actions as a string for logging</returns>
        [FunctionName("ProcessStateData")]
        public static async Task<IActionResult> FnProcessStateData([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = null)] HttpRequest req, ILogger log, ExecutionContext context)
        {
            log.LogInformation("HTTP based trigger fired for ProcessStateData");
            return await ProcessStateData(log, context, "http");
        }

        /// <summary>
        /// Common function to Process Small Region Data regardless of trigger
        /// </summary>
        private static async Task<IActionResult> ProcessStateData(ILogger log, ExecutionContext context, string triggerType)
        {
            const string FUNCTION_NAME = "ProcessStateData";
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
            var msg = "";
            sw.Start();

            System.Text.StringBuilder sbResponse = new System.Text.StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Started via {triggerType} at: {DateTime.Now}";
            log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            try
            {
                //get config data from appSettings.json
                msg = $"{FUNCTION_NAME}: Getting config data...";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);
                IConfigurationRoot config = ConfigUtil.GetConfig(context);

                msg = $"{FUNCTION_NAME}: Updating: {config["SmipSettings:GraphQLEndpoint"]}";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);

                //do the work
                var processor = new EIAUtility(config, log);
                sbResponse = await processor.ProcessStateData(sbResponse, FUNCTION_NAME, sw);
            }
            catch (Exception ex)
            {
                msg = $"{FUNCTION_NAME}: An exception occurred: {ex.Message}";
                log.LogCritical(ex, msg);
                sbResponse.AppendLine(msg);
            }
            finally
            {
                msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
                log.LogInformation(msg);
                sbResponse.AppendLine(msg);
            }

            //show the user how the data was processed.  
            return new OkObjectResult(sbResponse.ToString());
        }

        #endregion

        #region Country Data Functions
        /// <summary>
        /// Timer based function to process Country data. 
        /// Kick off daily.
        /// 0 35 1 * * * == 1.30am every day
        /// </summary>
        /// <remarks>Reference on timer expression: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-csharp#ncrontab-expressions</remarks>
        [FunctionName("ProcessCountryDataTimer")]
        public static async Task FnTimerProcessCountryData([TimerTrigger("0 35 1 * * *", RunOnStartup = false)] TimerInfo myTimer, ILogger log, ExecutionContext context)
        {
            log.LogInformation("Timer based trigger fired for ProcessCountryData");
            await ProcessCountryData(log, context, "timer");
        }

        [FunctionName("ProcessCountryData")]
        public static async Task<IActionResult> FnProcessCountryData([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = null)] HttpRequest req, ILogger log, ExecutionContext context)
        {
            log.LogInformation("HTTP based trigger fired for ProcessCountryData");
            return await ProcessCountryData(log, context, "http");
        }

        public static async Task<IActionResult> ProcessCountryData(ILogger log, ExecutionContext context, string triggerType)
        {
            const string FUNCTION_NAME = "ProcessCountryData";
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
            var msg = "";
            sw.Start();

            System.Text.StringBuilder sbResponse = new System.Text.StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Started via {triggerType} at: {DateTime.Now}";
            log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            try
            {
                //get config data from appSettings.json
                msg = $"{FUNCTION_NAME}: Getting config data...";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);
                IConfigurationRoot config = ConfigUtil.GetConfig(context);

                msg = $"{FUNCTION_NAME}: Updating: {config["SmipSettings:GraphQLEndpoint"]}";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);


                //do the work
                var processor = new EIAUtility(config, log);
                sbResponse = await processor.ProcessCountryData(sbResponse, FUNCTION_NAME, sw);
            }
            catch (Exception ex)
            {
                msg = $"{FUNCTION_NAME}: An exception occurred: {ex.Message}";
                log.LogCritical(ex, msg);
                sbResponse.AppendLine(msg);
            }
            finally
            {
                msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
                log.LogInformation(msg);
                sbResponse.AppendLine(msg);
            }

            //show the user how the data was processed.  
            return new OkObjectResult(sbResponse.ToString());
        }
        #endregion

        #region Watt-Time Functions 

        /// <summary>
        /// Timer based trigger for common watt time data function
        /// Kick off daily.
        /// 0 1 * * * * == 1 minutes past every hour of the day
        /// 0 */10 * * * * == 6 times an hour - at second 0 of every 10th minute of every hour of each day
        /// </summary>
        /// <remarks>Reference on timer expression: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-csharp#ncrontab-expressions</remarks>
        [FunctionName("ProcessWattTimeDataTimer")]
        public static async Task FnTimerProcessWattTimeData([TimerTrigger("0 */10 * * * *", RunOnStartup = false)] TimerInfo myTimer, ILogger log, ExecutionContext context)
        {
            log.LogInformation("Timer based trigger fired for ProcessWattTimeData");
            await ProcessWattTimeData(log, context, "timer");
        }

        [FunctionName("ProcessWattTimeData")]
        public static async Task<IActionResult> FnProcessWattTimeData([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = null)] HttpRequest req, ILogger log, ExecutionContext context)
        {
            log.LogInformation("HTTP based trigger fired for ProcessWattTimeData");
            return await ProcessWattTimeData(log, context, "http");
        }

        public static async Task<IActionResult> ProcessWattTimeData(ILogger log, ExecutionContext context, string triggerType)
        {
            const string FUNCTION_NAME = "ProcessWattTimeData";
            System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
            var msg = "";
            sw.Start();

            System.Text.StringBuilder sbResponse = new System.Text.StringBuilder();

            //put a starting message
            msg = $"{FUNCTION_NAME}: Started via {triggerType} at: {DateTime.Now}";
            log.LogInformation(msg);
            sbResponse.AppendLine(msg);

            try
            {
                //get config data from appSettings.json
                msg = $"{FUNCTION_NAME}: Getting config data...";
                log.LogTrace(msg);
                sbResponse.AppendLine(msg);
                IConfigurationRoot config = ConfigUtil.GetConfig(context);

                //do the work
                var processor = new WattTimeUtility(config, log);
                sbResponse = await processor.ProcessWattTimeData(sbResponse, FUNCTION_NAME, sw);
            }
            catch (Exception ex)
            {
                msg = $"{FUNCTION_NAME}: An exception occurred: {ex.Message}";
                log.LogCritical(ex, msg);
                sbResponse.AppendLine(msg);
            }
            finally
            {
                msg = $"{FUNCTION_NAME}: Finished...{DateTime.Now}...Duration:{sw.Elapsed.TotalSeconds} seconds";
                log.LogInformation(msg);
                sbResponse.AppendLine(msg);
            }

            //show the user how the data was processed.  
            return new OkObjectResult(sbResponse.ToString());
        }

        #endregion

    }
}
