const {
    OPCUAClient,
    AttributeIds,
    TimestampsToReturn,
    StatusCodes,
    DataType
} = require("node-opcua");
const fetch = require('node-fetch');

//UA Server
const endpointUrl = "opc.tcp://opcuademo.sterfive.com:26543";
const nodeId = "ns=1;i=1002";

//SMIP Instance
//  Establish this info using your platform instance, see https://github.com/cesmii/API/blob/main/Docs/jwt.md
const instanceGraphQLEndpoint = "https://demo.cesmii.net/graphql";
var currentBearerToken = "Bearer GETTHISFROMYOURPLATFORMINSTANCE";
const clientId = "demo";
const clientSecret = "demo";
const userName = "PLATFORMUSERTOWORKAS";
const role = "demo_owner";

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

                var newVal = dataValue.value.value;
                console.log("New Value=", newVal);
                //TODO: Make fix time stamp, need to see GraphQL response for debugging
                var smpQuery = JSON.stringify({
                    query : `mutation {
                        replaceTimeSeriesRange(
                            input: {
                              attributeOrTagId: "893"
                              entries: [
                                { timestamp: "2021-05-06T21:03:00Z", value: "${newVal}", status: "1" }
                              ]
                              startTime: "2021-05-06"
                              endTime: "2021-05-06"
                            }
                          ) {
                            clientMutationId
                            json
                          }
                    }`,
                });

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

    return await response.json();

    //TODO: Handle errors!
}
