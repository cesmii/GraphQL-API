using System;
using System.Collections.Generic;
using System.Text;

namespace CESMII.EnergyConsumption.Functions.Models
{
    internal class WattTimeDataPoint
    {
        public DateTime point_time { get; set; }
        public float value { get; set; }
        public int freqency { get; set; }
        public string market { get; set; }
        public string ba { get; set; }
        public string datatype { get; set; }
        public string version { get; set; } 

    }
}
