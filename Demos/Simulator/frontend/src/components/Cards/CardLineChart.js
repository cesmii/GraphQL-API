import ReactApexChart from "react-apexcharts";
import ApexCharts from 'apexcharts'
import React, { Component } from "react";
//import { doMain} from "index.js"
import { getConfigFileParsingDiagnostics } from "typescript";
import { gql, useQuery } from "@apollo/client";
const fetch = require('node-fetch');
const instanceGraphQLEndpoint = "https://sandbox.cesmii.net/graphql";
export default function CardChart({tank_volumesID, ymax}){
var last = 0
const color_set = ["#a5778a", "#a7f199", "#87ad86", "#cb3f93", "#cb7460","#9300c0", "#89cff0", "#3f3252", "#9f1141", "#6de137"];
//console.log("ids",tank_volumesID)
/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2FuZGJveF9yb19ncm91cCIsImV4cCI6MTYzNzA4MzE5MywidXNlcl9uYW1lIjoid2VuamllIiwiYXV0aGVudGljYXRvciI6InNhbmRib3giLCJhdXRoZW50aWNhdGlvbl9pZCI6IjEyOSIsImlhdCI6MTYzNzA4MTM5MiwiYXVkIjoicG9zdGdyYXBoaWxlIiwiaXNzIjoicG9zdGdyYXBoaWxlIn0.Da-zvXQqLXORsDpxIHHerZt-7ZAxkwMNGXOjjR-aFvQ";

/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */

var smpResponse = ""
const clientId = "cesmii_tank_demo";
const clientSecret = "8BvMcF3ibGqDjRm";
const userName = "Wenjie Liu";
const role = "sandbox_group";

let today = new Date().toISOString().slice(0, 10)
today +=  "T00:00:00+00:00"
console.log(today)
let new_day = new Date()
var tomorrow = new Date(new_day)
tomorrow.setDate(tomorrow.getDate() + 1)
tomorrow = tomorrow.toISOString().slice(0, 10) + "T00:00:00+00:00"
console.log("tomorrow", tomorrow)

//Forms and sends a GraphQL request (query or mutation) and returns the response
async function performGraphQLRequest(query, endPoint, bearerToken) {
    var opt = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: query
      }
    if (bearerToken && bearerToken != "")
        opt.headers.Authorization = bearerToken;
    const response = await fetch(endPoint, opt);
    return await response.json();

    //TODO: Handle errors!
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
async function getBearerToken() {

    // Step 1: Request a challenge
    var authResponse = await performGraphQLRequest(JSON.stringify({
        "query": " mutation {\
            authenticationRequest(input: \
              {authenticator:\"" + clientId + "\", \
              role: \"" + role + "\", \
              userName: \"" + userName + "\"})\
             { jwtRequest { challenge, message } } }"
      }), instanceGraphQLEndpoint);
    var challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
    console.log("Challenge received: " + challenge);

    // Step 2: Get token
    var challengeResponse = await performGraphQLRequest(JSON.stringify({
        "query": " mutation {\
            authenticationValidation(input: \
              {authenticator:\"" + clientId + "\", \
              signedChallenge: \"" + challenge + "|" + clientSecret + "\"})\
             { jwtClaim } }"
    }), instanceGraphQLEndpoint);

    var newJwtToken = challengeResponse.data.authenticationValidation.jwtClaim;
    return newJwtToken;

    //TODO: Handle errors!
}

//Main Program Function
async function doMain(tank) {
    console.log("Requesting Data from CESMII Smart Manufacturing Platform...")
    console.log();

    /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
    var smpQuery = JSON.stringify({
        query: `{
          getRawHistoryDataWithSampling(
            maxSamples: 0
            ids: ["${tank}"]
            startTime: "${today}"
            endTime: "${tomorrow}"
          ) {
            id
            floatvalue
            dataType
            ts
            status
          }
        }`,
      });
    smpResponse = await performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);

    if (JSON.stringify(smpResponse).indexOf("expired") != -1)
    {
        console.log("Bearer Token expired!");
        console.log("Attempting to retreive a new GraphQL Bearer Token...");
        console.log();

        //Authenticate
        var newTokenResponse = await getBearerToken(instanceGraphQLEndpoint);
        currentBearerToken = "Bearer " + newTokenResponse;

        //console.log("New Token received: " + JSON.stringify(newTokenResponse));
        console.log();

        //Re-try our data request, using the updated bearer token
        //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
        smpResponse = await performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);
    }


    last = smpResponse.data.getRawHistoryDataWithSampling.length - 1
    console.log("Response from SM Platform was... ");
    //console.log(JSON.stringify(smpResponse, null, 2));
    console.log("last", last);
    console.log("ok",parseFloat(smpResponse.data.getRawHistoryDataWithSampling[last].floatvalue));
    return parseFloat(smpResponse.data.getRawHistoryDataWithSampling[last].floatvalue);
}


//console.log("res",doMain(tank_volumesID[0]));

var lastDate = 0;

var data_groups = []
var TICKINTERVAL = 86400000
const DATA_POINT_AMOUNT = 10
var data1 = []
var data2 = []
var data3 = []
var data4 = []
var data5 = []
let XAXISRANGE = 777600000
var series1 = []
//var tank_amount = 5
//var tank_volumesID = ["8519", "8531", "8543", "8555", "8567"]



function getDayWiseTimeSeries(baseval, count, yrange, tank_amount) {
  var i = 0;
  while (i < count) {
    var x = baseval;
    var y = 0;
    data1.push({
      x, y
    });
    data2.push({
      x, y
    });
    data3.push({
      x, y
    });
    data4.push({
      x, y
    });
    data5.push({
      x, y
    });
    lastDate = baseval
    baseval += TICKINTERVAL;
    i++;
  }
  
  
  for(var j =0;j<tank_amount; j++){
    series1.push({data: data1.slice()});
  }
  console.log("first create", tank_amount, series1)
}



console.log("series at first",JSON.stringify(series1));





function getNewSeries(baseval, tank_volumesID) {
    var tank_amount = tank_volumesID.length;
    var newDate = baseval + TICKINTERVAL;
    lastDate = newDate

  var promises 
  promises = tank_volumesID.map((id) => {
    return doMain(id)
  })
  Promise.all(promises).then((resolutions) => {
    console.log("resolutions",resolutions)
    for(var j =0; j<tank_amount;j++){
        for(var k = 0; k< data1.length - 10; k++) {
        // IMPORTANT
        // we reset the x and y of the data which is out of drawing area
        // to prevent memory leaks
            series1[j].data.x = newDate - XAXISRANGE - TICKINTERVAL
            series1[j].data.y = 0
        }
        series1[j].data.push({
            x: newDate,
            y: resolutions[j]
          })

    }

  });

  
  }

    var tank_amount = tank_volumesID.length;
    console.log("len",tank_amount)
    const state = {   
      options: {
        chart: {
          id: 'realtime',
          height: 350,
          type: 'line',
          animations: {
            enabled: true,
            easing: 'linear',
            dynamicAnimation: {
              speed: 2000
            }
          },
          toolbar: {
            show: false
          },
          zoom: {
            enabled: false
          }
        },
        colors: color_set,
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: 'smooth'
        },

        markers: {
          size: 0
        },

        xaxis: {
          labels: {
            show: false,
            format: 'mm/ss',
          },
          type: 'datetime',
          range: XAXISRANGE/9*5,
        },
        yaxis: {
          max: ymax
        },
        legend: {
          show: false
        },
      },
    
    
    };

    getDayWiseTimeSeries(new Date('11 Feb 2017 GMT').getTime(), 10, {
        min: 10,
        max: 30
      }, tank_amount)

      console.log("first seires1 here", series1);
    React.useEffect(() => {
    
        const intervalId = setInterval(() => {
            
          getNewSeries(lastDate, tank_volumesID);
          console.log("seires1 here", series1);
          ApexCharts.exec('realtime', 'updateSeries', 
      series1)
        }, 2000) // in milliseconds
        return () => clearInterval(intervalId)
      }, [])



    return (
      <div>
        <div id="chart">
          <ReactApexChart options={state.options} series={series1} type="line" height={350} />
        </div>
        <div id="html-dist"></div>
      </div>
    );

};




