import React from "react";

// components

import CardChart from "components/Cards/CardLineChart1.js";
import CardBarChart from "components/Cards/CardBarChart.js";
import HeaderStats_oneTank from "components/Headers/HeaderStats_oneTank.js";
import CardPageVisits from "components/Cards/CardPageVisits.js";
import CardSocialTraffic from "components/Cards/CardSocialTraffic.js";
import {one_tank_info} from "index.js";
//console.log(one_tank_info)
export default function Demo_oneTank() {
  function create_chart(index){
    if (index==0){
      return(
          <CardChart 
        tank_volumesID={one_tank_info}
        ymax = {80}
          />
      )
    }
  }
  return (
    <>
      <HeaderStats_oneTank />
      <div className="flex flex-wrap">
        
        <div className="w-full xl:w-8/12 mb-12 xl:mb-0 px-4">
        {one_tank_info.map((tank,index)=>create_chart(index))}
        </div>

      </div>
      {/*<div className="flex flex-wrap mt-4">
        <div className="w-full xl:w-8/12 mb-12 xl:mb-0 px-4">
          <CardPageVisits />
        </div>
        <div className="w-full xl:w-4/12 px-4">
          <CardSocialTraffic />
        </div>
      </div>*/}
    </>
  );
}
