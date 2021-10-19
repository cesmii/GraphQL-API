import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch, Redirect } from "react-router-dom";
import { ApolloProvider, ApolloClient, createHttpLink, InMemoryCache } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";

import "@fortawesome/fontawesome-free/css/all.min.css";
import "assets/styles/tailwind.css";

// layouts

import Admin from "layouts/Admin.js";
import Auth from "layouts/Auth.js";

// views without layouts

import Landing from "views/Landing.js";
import Profile from "views/Profile.js";
import Index from "views/Index.js";

const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";
console.log("before http");
const httpLink = createHttpLink({
  uri: instanceGraphQLEndpoint,
});
console.log("before auth");

const tempvar = 99999;
const tank_volumesID = [];
const tank_sizes = [];
const tank_names = [];
const tank_info = [];
const tank_flowrateID = [];
const tank_temperatureID = [];
const tank_serialNumber = [];
var tank_colors = [];
let one_tank_info = [];


const authLink = setContext((_, { headers }) => {
  // get the authentication token from local storage if it exists
  const token = localStorage.getItem("token");
  // return the headers to the context so httpLink can read them
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    },
  };
});
console.log("after auth");
const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
console.log("after client");

/* Dependenices to install via npm
 - node-fetch
 Tested with Node.JS 12.6.3
*/
const fetch = require("node-fetch");

/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZGVtb19yb19ncm91cCIsImV4cCI6MTYyNzQwNjM2OCwidXNlcl9uYW1lIjoid2VuamllIiwiYXV0aGVudGljYXRvciI6IkRlbW8gQ0VTTUlJIiwiYXV0aGVudGljYXRpb25faWQiOiIxMjQ3IiwiaWF0IjoxNjI3NDA0NTY3LCJhdWQiOiJwb3N0Z3JhcGhpbGUiLCJpc3MiOiJwb3N0Z3JhcGhpbGUifQ.x_6TeD9EggiQlcrXnWDtSjSVKPVxgsTjBB6lcwX8K7U";
/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */
const clientId = "cesmii_tank_demo";
const clientSecret = "8BvMcF3ibGqDjRm";
const userName = "cesmiihq";
const role = "demo_owner";

//Call main program function
doMain();

//Forms and sends a GraphQL request (query or mutation) and returns the response
async function performGraphQLRequest(query, endPoint, bearerToken) {
  let opt = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: query,
  };
  if (bearerToken && bearerToken != "") opt.headers.Authorization = bearerToken;
  const response = await fetch(endPoint, opt);
  return await response.json();

  //TODO: Handle errors!
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
async function getBearerToken() {
  // Step 1: Request a challenge
  const authResponse = await performGraphQLRequest(
    JSON.stringify({
      query:
        ' mutation {\
            authenticationRequest(input: \
              {authenticator:"' +
        clientId +
        '", \
              role: "' +
        role +
        '", \
              userName: "' +
        userName +
        '"})\
             { jwtRequest { challenge, message } } }',
    }),
    instanceGraphQLEndpoint
  );
  const challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
  console.log("Challenge received: " + challenge);

  // Step 2: Get token
  const challengeResponse = await performGraphQLRequest(
    JSON.stringify({
      query:
        ' mutation {\
            authenticationValidation(input: \
              {authenticator:"' +
        clientId +
        '", \
              signedChallenge: "' +
        challenge +
        "|" +
        clientSecret +
        '"})\
             { jwtClaim } }',
    }),
    instanceGraphQLEndpoint
  );

  const newJwtToken = challengeResponse.data.authenticationValidation.jwtClaim;

  // Set localstorage for Apollo
  localStorage.setItem("token", newJwtToken);

  // TODO: Remove local storage token after logging out of the app

  return newJwtToken;

  //TODO: Handle errors!
}

//Main Program Function
async function doMain() {
  console.log("Requesting Data from CESMII Smart Manufacturing Platform...");
  console.log();

  /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
  const smpQuery = JSON.stringify({
    query: `{
          equipments( filter:{typeId: {equalTo: "1042"}}
            ) {
            id
            displayName
            attributes{
              displayName
              id
              floatValue
              stringValue
            }
          }
        }`,
  });

  let smpResponse = await performGraphQLRequest(
    smpQuery,
    instanceGraphQLEndpoint,
    currentBearerToken
  );

  if (JSON.stringify(smpResponse).indexOf("expired") != -1 || JSON.stringify(smpResponse).indexOf("malformed") != -1) {
    console.log("Bearer Token expired!");
    console.log("Attempting to retreive a new GraphQL Bearer Token...");
    console.log();

    //Authenticate
    const newTokenResponse = await getBearerToken(instanceGraphQLEndpoint);
    currentBearerToken = "Bearer " + newTokenResponse;

    console.log("New Token received: " + JSON.stringify(newTokenResponse));
    console.log();

    //Re-try our data request, using the updated bearer token
    //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
    smpResponse = await performGraphQLRequest(
      smpQuery,
      instanceGraphQLEndpoint,
      currentBearerToken
    );
  }

  console.log("Response from SM Platform was... ");
  for (let ele of smpResponse.data.equipments){
    console.log(ele);
    const attributes = ele.attributes;
    let temp = {"name": ele.displayName};
    let one = false;
    for (let attribute of attributes){
      if(attribute.displayName=="size") temp["size"] = attribute.floatValue;
      else if(attribute.displayName=="volume") temp["volumeID"] = attribute.id;
      else if(attribute.displayName=="flowrate") temp["flowrateID"] = attribute.id;
      else if(attribute.displayName=="temperature") temp["temperatureID"] = attribute.id;
      else if(attribute.displayName=="one_tank_model" && attribute.floatValue==1) one = true;
      else if(attribute.displayName=="serialNumber") temp["serialNumber"] = attribute.stringValue;
    }
    if (one) {
      one_tank_info=[temp["flowrateID"], temp["volumeID"], temp["temperatureID"]];
      one = false;
    }
    else{
      tank_info.push(temp);
    }
    
    }

  tank_info.sort(function(a, b){
    let x = a.name;
    let y = b.name;
    if (x < y) {return -1;}
    if (x > y) {return 1;}
    return (x<y);
  });

  for (let tank of tank_info){
    tank_names.push(tank.name);
    tank_sizes.push(tank.size);
    tank_volumesID.push(tank.volumeID);
    tank_flowrateID.push(tank.flowrateID);
    tank_temperatureID.push(tank.temperatureID);
    tank_serialNumber.push(tank.serialNumber);

  }
  var tank_amount = tank_volumesID.length;
  var randomColor = '';
  for(var i=0;i<tank_amount;i++){
    randomColor = '#'+Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
    tank_colors.push(randomColor);
  }
  console.log(one_tank_info);
  console.log(tank_info);
  //console.log(JSON.stringify(smpResponse, null, 2));
  console.log(tank_names);
  console.log(tank_sizes);
  console.log(tank_volumesID);
  console.log(tank_flowrateID);
  console.log(tank_temperatureID);
  console.log(tank_serialNumber);
}

ReactDOM.render(
  <ApolloProvider client={client}>
    <BrowserRouter>
      <Switch>
        {/* add routes with layouts */}
        <Route path="/admin" component={Admin} />
        <Route path="/auth" component={Auth} />
        {/* add routes without layouts */}
        <Route path="/landing" exact component={Landing} />
        <Route path="/profile" exact component={Profile} />
        <Route path="/" exact component={Index} />
        {/* add redirect for first page */}
        <Redirect from="*" to="/" />
      </Switch>
    </BrowserRouter>
  </ApolloProvider>,
  document.getElementById("root")
);

export {tempvar, tank_names, tank_sizes, tank_volumesID, tank_flowrateID, tank_temperatureID, tank_serialNumber, one_tank_info, tank_colors, doMain} ;
