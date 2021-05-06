# node-opcua-sample

a simple OPCUA sample client to demonstrate how to use the [node-opcua](https://github.com/node-opcua/node-opcua) SDK and send data to the SMIP via GraphQL.

    + clone the repo
    + enter the directory
    + run `npm install`
    + run `node ua-to-graphql.js`

Note: This project was forked from https://github.com/node-opcua/node-opcua-sample -- which apparently has an old version of lodash with some security vulnerabilities. If you intend to use in production, you may wish to update the upstream repo, or try out other UA SDKs.

## More information 

![NodeOPCUA By Example](https://d2sofvawe08yqg.cloudfront.net/node-opcuabyexample/hero2x?1573652947)

The book [NodeOPCUA by example](https://leanpub.com/node-opcuabyexample) provides a comprehensive set of example that goes beyond the simple example provided here.

The [GraphQL website](https://graphql.org/) has more information on the standard. This repo has documentation on the schema used in the CESMII SMIP.
