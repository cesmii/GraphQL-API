using System;
using System.Collections.Generic;
using System.Text;
using Microsoft.Extensions.Configuration;
using CESMII.EnergyConsumption.Functions.Config.Models;

namespace CESMII.EnergyConsumption.Functions.Config
{
    /// <summary>
    /// Helper class to bind parts of appSettings to an object we can use in the code. 
    /// </summary>
    public class ConfigUtil
    {
        private readonly IConfiguration _configuration;

        public ConfigUtil(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public SMIPConfig SmipSettings
        {
            get
            {
                var result = new SMIPConfig();
                _configuration.GetSection("SmipSettings").Bind(result);
                return result;
            }
        }

        public DoeConfig DoeSettings
        {
            get
            {
                var result = new DoeConfig();
                _configuration.GetSection("DoeSettings").Bind(result);
                return result;
            }
        }

        public DoeConfig WattTimeSettings
        {
            get
            {
                var result = new DoeConfig();
                _configuration.GetSection("WattTimeSettings").Bind(result);
                return result;
            }
        }


        /// <summary>
        /// Load the appSettings file(s) with application settings. 
        /// </summary>
        /// <param name="context"></param>
        /// <returns></returns>
        public static IConfigurationRoot GetConfig(Microsoft.Azure.WebJobs.ExecutionContext context)
        {
            var config = new ConfigurationBuilder()
               .SetBasePath(context.FunctionAppDirectory)
               // This gives you access to your application settings 
               //.AddJsonFile("appSettings.json", optional: true, reloadOnChange: true)
               // This gives you access to an environment specific application settings 
               //.AddJsonFile($"appSettings.{Environment.GetEnvironmentVariable("Environment")}.json", optional: true, reloadOnChange: true)
               // This is what actually gets you the application settings in Azure (and local.settings.json)
               .AddEnvironmentVariables()
               .Build();
            return config;
        }

    }
}

