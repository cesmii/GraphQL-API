import { color } from "d3-color";
import { interpolateRgb } from "d3-interpolate";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

// components

import LiquidFillGauge from "react-liquid-gauge";

export default function LiquidGauge({
  tankid,
  val,
  tank_size,
  unit,
  gaugeTitle,
  state,
  startColor,
  endColor,
  statSubtitle,
  statTitle,
  statArrow,
  statPercent,
  statPercentColor,
  statDescripiron,
  statIconName,
  statIconColor,
}) {
  const radius = Math.round(Math.sqrt(tank_size/20.0) * 50);
  const interpolate = interpolateRgb({ startColor }, { endColor });
  const fillColor = interpolate({ state } / 100);
  const gradientStops = [
    {
      key: "0%",
      stopColor: color(fillColor).darker(0.5).toString(),
      stopOpacity: 1,
      offset: "0%",
    },
    {
      key: "50%",
      stopColor: fillColor,
      stopOpacity: 0.75,
      offset: "50%",
    },
    {
      key: "100%",
      stopColor: color(fillColor).brighter(0.5).toString(),
      stopOpacity: 0.5,
      offset: "100%",
    },
  ];

  return (
    <>
      <div className="flex-child min-w-0 bg-white rounded shadow-lg">
        <div className="flex-auto p-4">
          <div className="flex flex-nowrap">
            <div className="relative w-full pr-4 max-w-full flex-grow flex-1">
              <h5 className="text-black uppercase font-bold text-s">
                {gaugeTitle}
              </h5>
              <span className="font-semibold text-xl text-blueGray-700">
                <LiquidFillGauge
                  style={{ margin: "0 auto" }}
                  width={radius * 2}
                  height={radius * 2}
                  value={state}
                  val={val}
                  unit = {unit}
                  textSize={1}
                  textOffsetX={0}
                  textOffsetY={0}
                  textRenderer={(props) => {
                    const value = props.val;
                    const radius = Math.min(props.height / 2, props.width / 2);
                    const textPixels = (props.textSize * radius) / 2;
                    const valueStyle = {
                      fontSize: textPixels,
                    };
                    const percentStyle = {
                      fontSize: textPixels * 0.6,
                    };

                    return (
                      <tspan>
                        <tspan className="value" style={valueStyle}>
                          {value}
                        </tspan>
                        <tspan style={percentStyle}>{props.unit}</tspan>
                      </tspan>
                    );
                  }}
                  riseAnimation
                  waveAnimation
                  waveFrequency={2}
                  waveAmplitude={1}
                  gradient
                  gradientStops={gradientStops}
                  circleStyle={{
                    fill: fillColor,
                  }}
                  waveStyle={{
                    fill: fillColor,
                  }}
                  textStyle={{
                    fill: color("#444").toString(),
                    fontFamily: "Arial",
                  }}
                  waveTextStyle={{
                    fill: color("#fff").toString(),
                    fontFamily: "Arial",
                  }}
                  onClick={() => {
                    this.setState({ value: Math.random() * 100 });
                  }}
                />
              </span>
            </div>
            <div className="relative w-auto pl-4 flex-initial">
              <div
                className={
                  "text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 shadow-lg rounded-full " +
                  statIconColor
                }
              >
                <i className={statIconName}></i>
              </div>
            </div>
          </div>
          <p className="text-sm text-blueGray-700 mt-4">
            <span className={statPercentColor + " mr-2"}>
      
              ID
            </span>
            <span className="whitespace-nowrap">{tankid}</span>
          </p>
        </div>
      </div>
    </>
  );
}

LiquidGauge.defaultProps = {
  tankid: '1319',
  unit: "",
  gaugeTitle: "TANK 1 FILL LEVEL",
  val: 20,
  tank_size: 20,
  state: Math.random() * 100,
  startColor: "#6495ed", // cornflowerblue
  endColor: "#dc143c", // crimson
  statSubtitle: "Traffic",
  statTitle: "350,897",
  statArrow: "up",
  statPercent: "3.48",
  statPercentColor: "text-emerald-500",
  statDescripiron: "Since last month",
  statIconName: "far fa-chart-bar",
  statIconColor: "bg-red-500",
};

LiquidGauge.propTypes = {
  unit: PropTypes.string,
  tankid: PropTypes.string,
  val: PropTypes.number,
  tank_size: PropTypes.number,
  gaugeTitle: PropTypes.string,
  state: PropTypes.number,
  startColor: PropTypes.string,
  endColor: PropTypes.string,
  statSubtitle: PropTypes.string,
  statTitle: PropTypes.string,
  statArrow: PropTypes.oneOf(["up", "down"]),
  statPercent: PropTypes.string,
  // can be any of the text color utilities
  // from tailwindcss
  statPercentColor: PropTypes.string,
  statDescripiron: PropTypes.string,
  statIconName: PropTypes.string,
  // can be any of the background color utilities
  // from tailwindcss
  statIconColor: PropTypes.string,
};
