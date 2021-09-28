import ReactApexChart from "react-apexcharts";
import ApexCharts from 'apexcharts'
import React, { Component } from "react";
import { gql, useQuery } from "@apollo/client";
const fetch = require('node-fetch');
const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";
var last = 0
var tanks = [1319, 1325, 1283, 1290, 1296, 1302, 1308];
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
//Call main program function
//doMain();

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
            startTime: "2021-09-24 00:00:00+00"
            endTime: "2021-09-29 00:12:00+00"
            filter: {ts: {greaterThan: "2021-09-27 00:00:00+00"}}
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

        console.log("New Token received: " + JSON.stringify(newTokenResponse));
        console.log();

        //Re-try our data request, using the updated bearer token
        //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
        smpResponse = await performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken);
    }


    last = smpResponse.data.getRawHistoryDataWithSampling.length - 1
    console.log("Response from SM Platform was... ");
    console.log(JSON.stringify(smpResponse, null, 2));
    console.log();
    console.log("ok",parseFloat(smpResponse.data.getRawHistoryDataWithSampling[last].floatvalue));
    return parseFloat(smpResponse.data.getRawHistoryDataWithSampling[1].floatvalue);
}
doMain("6429")

var lastDate = 0;

var data_groups = []
var TICKINTERVAL = 86400000
const DATA_POINT_AMOUNT = 10
var data1 = []
var data2 = []
let XAXISRANGE = 777600000




function getDayWiseTimeSeries(baseval, count, yrange) {
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
    lastDate = baseval
    baseval += TICKINTERVAL;
    i++;
  }
}

getDayWiseTimeSeries(new Date('11 Feb 2017 GMT').getTime(), 10, {
  min: 10,
  max: 30
})

function getNewSeries(baseval, yrange) {
  var newDate = baseval + TICKINTERVAL;
  lastDate = newDate
  var temp = doMain("6429");
  for(var i = 0; i< data1.length - 10; i++) {
    // IMPORTANT
    // we reset the x and y of the data which is out of drawing area
    // to prevent memory leaks
    data1[i].x = newDate - XAXISRANGE - TICKINTERVAL
    data1[i].y = 0
    data2[i].x = newDate - XAXISRANGE - TICKINTERVAL
    data2[i].y = 0
  }

  data1.push({
    x: newDate,
    y: parseFloat(smpResponse.data.getRawHistoryDataWithSampling[last].floatvalue)
  })
  data2.push({
    x: newDate,
    y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min
  })
}



class CardLineChart extends Component{
  constructor(props) {
    super(props);

    this.state = {
    
      series: [{
        name: "a real tank",
        data: data1.slice()
      },
      {
        name: "a random line",
        data: data2.slice()
      }],
      options: {
        chart: {
          id: 'realtime',
          height: 350,
          type: 'line',
          animations: {
            enabled: true,
            easing: 'linear',
            dynamicAnimation: {
              speed: 1000
            }
          },
          toolbar: {
            show: false
          },
          zoom: {
            enabled: false
          }
        },
        colors: ['#77B6EA', '#545454'],
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
            format: 'mm/ss',
          },
          type: 'datetime',
          range: XAXISRANGE,
        },
        yaxis: {
          max: 35
        },
        legend: {
          show: false
        },
      },
    
    
    };
  }


  componentDidMount() {
    window.setInterval(() => {
      getNewSeries(lastDate, {
        min: 0,
        max: 30
      })
      
      ApexCharts.exec('realtime', 'updateSeries', [
        {data: data1}, 
        {data: data2}, 
    ])
      
    }, 1000)
  }


  render() {
    return (
      <div>
        <div id="chart">
          <ReactApexChart options={this.state.options} series={this.state.series} type="line" height={350} />
        </div>
        <div id="html-dist"></div>
      </div>
    );
  }
}



export default CardLineChart;
