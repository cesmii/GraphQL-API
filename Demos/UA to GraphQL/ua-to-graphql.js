const {
    OPCUAClient,
    AttributeIds,
    TimestampsToReturn,
    StatusCodes,
    DataType
} = require("node-opcua");
const fetch = require('node-fetch');

//UA Server
const endpointUrl = "opc.tcp://milo.digitalpetri.com:62541/milo";	//https://github.com/digitalpetri/opc-ua-demo-server
const nodeId = "ns=2;s=Dynamic/RandomFloat";

//SMIP Instance
//  Establish this info using your platform instance, see https://github.com/cesmii/API/blob/main/Docs/jwt.md
const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";

var currentBearerToken = "Bearer GETBEARERTOKENFROMPLATFORMINSTANCE";

const clientId = "demo";
const clientSecret = "demo";
const userName = "YOURUSERNAME";
const role = "demo_owner";
const attributeOrTagId = 893;	//See "Finding IDs" in https://github.com/cesmii/API/blob/main/Docs/mutations.md

async function main() {

    try {

        const client = OPCUAClient.create({
            endpoint_must_exist: false,
            connectionStrategy: {
                maxRetry: 2,
                initialDelay: 2000,
                maxDelay: 10 * 1000
            }
        });
        client.on("backoff", () => console.log("retrying connection"));


        await client.connect(endpointUrl);

        const session = await client.createSession();

        const browseResult = await session.browse("RootFolder");

        console.log(browseResult.references.map((r) => r.browseName.toString()).join("\n"));

        const dataValue = await session.read({ nodeId, attributeId: AttributeIds.Value });
        console.log(` value = ${dataValue.value.value.toString()}`);

        // step 5: install a subscription and monitored item
        const subscription = await session.createSubscription2({
            requestedPublishingInterval: 1000,
            requestedLifetimeCount: 100, // 1000ms *100 every 2 minutes or so
            requestedMaxKeepAliveCount: 10,// every 10 seconds
            maxNotificationsPerPublish: 10,
            publishingEnabled: true,
            priority: 10
        });

        subscription
            .on("started", () => console.log("subscription started - subscriptionId=", subscription.subscriptionId))
            .on("keepalive", () => console.log("keepalive"))
            .on("terminated", () => console.log("subscription terminated"));


        const monitoredItem = await subscription.monitor({
            nodeId: nodeId,
            attributeId: AttributeIds.Value
        },
            {
                samplingInterval: 1000,
                discardOldest: true,
                queueSize: 10
            }, TimestampsToReturn.Both);


        monitoredItem.on("changed", function (dataValue) {

                var newVal = dataValue.value.value * 100;	//Multiplied by 100 for cooler looking trend lines
				var newTS = makeUTCTimeStamp();
                console.log("New Value=", newVal, "TimeStamp=", newTS);
                var smpQuery = JSON.stringify({
                    query : `mutation {
                        replaceTimeSeriesRange(
                            input: {
                              attributeOrTagId: "${attributeOrTagId}",
                              entries: [
                                { timestamp: "${newTS}", value: "${newVal}", status: "1" }
                              ]
                            }
                          ) {
                            clientMutationId
                            json
                          }
                    }`,
                });
				//console.log("Debug Query:", smpQuery);
                performGraphQLRequest(smpQuery, instanceGraphQLEndpoint, currentBearerToken).then(function(res){
                    console.log("SMIP response: " + JSON.stringify(res));
                });

            });

        await new Promise((resolve) => setTimeout(resolve, 5000));

        await subscription.terminate();

        const statusCode = await session.write({
            nodeId: nodeId,
            attributeId: AttributeIds.Value,
            value: {
                statusCode: StatusCodes.Good,
                sourceTimestamp: new Date(),
                value: {
                    dataType: DataType.Double,
                    value: 25.0
                }
            }
        });
        console.log("statusCode = ", statusCode.toString());

        console.log(" closing session");
        await session.close();

        await client.disconnect();
    }
    catch (err) {
        console.log("Error !!!", err);
        process.exit();
    }
}

main();

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
	//console.log("Debug Response:", response);
    return await response.json();

    //TODO: Handle errors, including token expiry. See: https://github.com/cesmii/API/tree/main/Samples/Javascript
}

function makeUTCTimeStamp() {
	//Must be like: 2021-05-11T15:03:00Z
	var d = new Date();
	var u = d.getUTCFullYear() + "-" + zeroLead(d.getUTCMonth()+1) + "-" + zeroLead(d.getUTCDate()) + "T" + zeroLead(d.getUTCHours()) + ":" + zeroLead(d.getUTCMinutes()) + ":" + zeroLead(d.getUTCSeconds()) + "Z";
	return u;
}

function zeroLead(val) {
	if (val < 10)
		return "0" + val;
	else
		return val;
}
