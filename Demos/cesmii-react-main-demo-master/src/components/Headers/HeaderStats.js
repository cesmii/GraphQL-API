import React from "react";

// components

import CardStats from "components/Cards/CardStats.js";
import LiquidGauge from "components/Gauges/LiquidGauge.js";

import { gql, useQuery } from "@apollo/client";
import {tempvar, tank_names, tank_sizes, tank_volumesID, tank_serialNumber} from "index.js"

export default function HeaderStats() {
  // All Tanks
  // let tanks = ["1319", "1325", "1283", "1290", "1296", "1302", "1308", "2129"];

  // 6 tanks
  console.log(tempvar)
  
  const type_id = "1042"
  console.log(tank_names)
  console.log(tank_sizes)
  console.log(tank_volumesID)
  // Tanks 2 & 5
  // let tanks = ["1283", "1302"];

  //let tanks = ["2129", "2130", "2131"];


  const GET_TANK_DATA = gql`
    query Tank($tank: [BigInt]) {
      getRawHistoryDataWithSampling(
        ids: $tank
        startTime: "2021-08-24 00:00:00+00"
        endTime: "2021-09-29 00:00:00+00"
        maxSamples: 1
      ) {
        floatvalue
      }
    }
  `;




  /*const GET_TANKS = gql`
    query Tank($typeid: BigInt) {
      equipments( filter:{typeId: {equalTo: $typeid}}
      ) {
        displayName
        id
        attributes {
        displayName
        id
        }
      }
    }
  `;

  const { loading1, error1, tanks_info } = useQuery(GET_TANKS, {
    variables: {type_id},
  });

  if (loading1) {
    console.log("we are loading");
    return null;
  }
  if (error1) return `Error! ${error1}`;
  console.log(
    "got the info",
    JSON.stringify(tanks_info)
  );
  */




  function TankData(tank, index, divisor, unit_symbol, title) {
    console.log(`tank: ${tank}`);
    const { loading, error, data } = useQuery(GET_TANK_DATA, {
      variables: { tank },
      pollInterval: 1000,
    });

    if (loading) {
      console.log("we are loading");
      return null;
    }
    if (error) return `Error! ${error}`;
    console.log(
      "data.getRawHistoryDataWithSampling[1].floatvalue",
      JSON.stringify(data.getRawHistoryDataWithSampling, null, 2)
    );
    return (
      <div className="w-full lg:w-6/12 xl:w-4/12 px-2 pb-4" key={index}>
        <LiquidGauge
          key={index}
          tankid={tank_serialNumber[index]}
          gaugeTitle={title}
          unit = {unit_symbol}
          tank_size = {divisor}
          val= {data.getRawHistoryDataWithSampling[0].floatvalue}
          state={ data.getRawHistoryDataWithSampling[0].floatvalue*100/divisor}
        />
      </div>
    );
  }


  



  return (
    <>
      {/* Header */}
      <div className="relative bg-lightBlue-200 md:pt-32 pb-32 pt-12 ">
        <div className="px-4 md:px-0 mx-auto w-full">
        <div className="flex flex-wrap ">
      {tank_volumesID.map((tank, index) => TankData(tank, index, tank_sizes[index], "L", tank_names[index]))}
            </div>
        </div>
      </div>
    </>
  );
}
