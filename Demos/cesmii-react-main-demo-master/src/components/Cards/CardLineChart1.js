import ReactApexChart from "react-apexcharts";
import ApexCharts from 'apexcharts'
import React, { Component } from "react";
//import { doMain} from "index.js"
import { getConfigFileParsingDiagnostics } from "typescript";
import { gql, useQuery } from "@apollo/client";
const fetch = require('node-fetch');
const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";
export default function CardChart({tank_volumesID, ymax}){
var last = 0
const color_set = ["#a5778a", "#a7f199", "#87ad86", "#cb3f93", "#cb7460","#9300c0", "#89cff0", "#3f3252", "#9f1141", "#6de137"];
//console.log("ids",tank_volumesID)
/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZGVtb19yb19ncm91cCIsImV4cCI6MTYyNjgwMjM4NCwidXNlcl9uYW1lIjoid2VuamllIiwiYXV0aGVudGljYXRvciI6IkRlbW8gQ0VTTUlJIiwiYXV0aGVudGljYXRpb25faWQiOiI0ODIiLCJpYXQiOjE2MjY4MDA1ODQsImF1ZCI6InBvc3RncmFwaGlsZSIsImlzcyI6InBvc3RncmFwaGlsZSJ9.PvskFkSFIc_qGB9lCwpjb6TCFQRK1ztb0bDdRIHFBvk";

/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */

var smpResponse = ""
const clientId = "cesmii_tank_demo";
const clientSecret = "8BvMcF3ibGqDjRm";
const userName = "cesmiihq";
const role = "demo_owner";



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
            maxSamples: 1
            ids: ["${tank}"]
            startTime: "2021-10-18 00:00:00+00"
            endTime: "2021-10-29 00:12:00+00"
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


console.log("res",doMain(tank_volumesID[0]));

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
    console.log("in getnew ", tank_volumesID, tank_volumesID.length)
    var tank_amount = tank_volumesID.length;
    var newDate = baseval + TICKINTERVAL;
    lastDate = newDate

  
  
  //this loop is for dynamic
    for(var j =0; j<tank_amount;j++){
        for(var k = 0; k< data1.length - 10; k++) {
        // IMPORTANT
        // we reset the x and y of the data which is out of drawing area
        // to prevent memory leaks
            series1[j].data.x = newDate - XAXISRANGE - TICKINTERVAL
            series1[j].data.y = 0
        }
    }

    (function loop(i) {
        console.log("loop")
        console.log("i0",i, tank_amount)
      if (i >= tank_amount) return; // all done
      console.log("i",i)
      doMain(tank_volumesID[i]).then((result) => {
        console.log("series in here changing",series1)
        series1[i].data.push({
          x: newDate,
          y: parseFloat(result)
        })
        loop(i+1);
      });
  })(0);




  
  
 /*
    doMain(tank_volumesID[0]).then((result) => {
      console.log(parseFloat(result))
      series1[0].data.push({
        x: newDate,
        y: parseFloat(result)
      })
  });
  
  doMain(tank_volumesID[1]).then((result) => {
    console.log(parseFloat(result))
    series1[1].data.push({
      x: newDate,
      y: parseFloat(result)
    })
  });
  
  doMain(tank_volumesID[2]).then((result) => {
    console.log(parseFloat(result))
    series1[2].data.push({
      x: newDate,
      y: parseFloat(result)
    })
  });
  doMain(tank_volumesID[3]).then((result) => {
    console.log(parseFloat(result))
    series1[3].data.push({
      x: newDate,
      y: parseFloat(result)
    })
  });
  doMain(tank_volumesID[4]).then((result) => {
    console.log(parseFloat(result))
    series1[4].data.push({
      x: newDate,
      y: parseFloat(result)
    })
  });
  */
      

  
  }

    //console.log(tank_volumesID.tank_volumesID);
    //console.log("len",tank_volumesID.tank_volumesID.length);

    //const[series2,setSeries2] = React.useState(series1);//[{data:data1.slice()},{data: data2.slice()}],//series1,
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
        title: {
          text: 'Dynamic Updating Chart',
          align: 'left'
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
          //console.log("val1", TankData(tank_volumesID[0]))
          //setSeries2(series1);
          ApexCharts.exec('realtime', 'updateSeries', 
      series1)
          //console.log("seires2 here", series2);
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




