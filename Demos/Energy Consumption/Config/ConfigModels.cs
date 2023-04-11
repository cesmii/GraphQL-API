using System;

namespace CESMII.EnergyConsumption.Functions.Config.Models
{
    /// <summary>
    /// Model which mimics the SMIP Settings in appSettings.json
    /// </summary>
    public class SMIPConfig
    {
        public string ClientId { get; set; }
        public string ClientSecret { get; set; }
        public string EquipmentId { get; set; }
        public string EquipmentParentId { get; set; }
    }

    /// <summary>
    /// Model which mimics the DoeSettings in appSettings.json
    /// </summary>
    public class DoeConfig
    {
        public string ApiKey { get; set; }
    }

}
