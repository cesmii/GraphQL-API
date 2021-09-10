import React from "react";

// components

import CardStats from "components/Cards/CardStats.js";
import LiquidGauge from "components/Gauges/LiquidGauge.js";

import { gql, useQuery } from "@apollo/client";
import {one_tank_info} from "index.js";

export default function HeaderStats() {
  // All Tanks
  // let tanks = ["1319", "1325", "1283", "1290", "1296", "1302", "1308", "2129"];

  // 6 tanks

  // Tanks 2 & 5
  // let tanks = ["1283", "1302"];

  //let tanks = ["2129", "2130", "2131"];
  const tag_names = ["Flowrate", "Fill Level", "Temperature"];
  const units = ["L/s", "L", "°F"];
  const divisors = [20.0, 20.0, 120.0]


  const GET_TANK_DATA = gql`
    query Tank($tank: [BigInt]) {
      getRawHistoryDataWithSampling(
        ids: $tank
        startTime: "2021-08-24 10:00:00+00"
        endTime: "2021-09-29 00:00:00+00"
        maxSamples: 1
      ) {
        floatvalue
      }
    }
  `;

  function TankData(tank, index, divisor, unit_symbol, title) {
    console.log(`tank: ${tank}`);
    const { loading, error, data } = useQuery(GET_TANK_DATA, {
      variables: { tank },
      pollInterval:1000,
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
          tankid={tank}
          gaugeTitle={title}
          unit = {unit_symbol}
          tank_size = {20.0}
          val= {data.getRawHistoryDataWithSampling[0].floatvalue}
          state={ data.getRawHistoryDataWithSampling[0].floatvalue*100/divisor}
        />
      </div>
    );
  }





  return (
    <>
      {/* Header */}
      <div className="relative bg-lightBlue-600 md:pt-32 pb-32 pt-12">
        <div className="px-4 md:px-0 mx-auto w-full">
        <div className="flex flex-wrap">
        {one_tank_info.map((tank, index) => TankData(tank, index, divisors[index], units[index], tag_names[index]))}
                 
      </div>
        </div>
      </div>
    </>
  );
}
