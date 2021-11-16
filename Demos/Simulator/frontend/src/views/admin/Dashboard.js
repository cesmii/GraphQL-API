import React from "react";
import {render} from 'react-dom';
// components

import CardChart from "components/Cards/CardLineChart.js";
import HeaderStats from "components/Headers/HeaderStats.js";
import {tank_volumesID} from "index.js"


export default function Dashboard() {


  function create_chart(index){
    if (index==0){
      return(
          <CardChart 
        tank_volumesID={tank_volumesID}
        ymax = {20}
          />
      )
    }
  }

  return (
    <>
      <HeaderStats />
      <div className="flex flex-wrap">
        
        <div className="w-full xl:w-8/12 mb-12 xl:mb-0 px-4">
        {tank_volumesID.map((tank,index)=>create_chart(index))}
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
