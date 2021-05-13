# UA-to-GraphQL Demo

This is a super slim example demonstrating how an OPC UA client subscription can be bridged to the SMIP using GraphQL.

## About the SMIP GraphQL Code

A small subsection of sample code from CESMII's [Javascript sample](https://github.com/cesmii/API/tree/main/Samples/Javascript) was used to illustrate a basic GraphQL mutation. The full sample should be referenced, since it implements handling token expiry. 
For this sample, you'll need a current Bearer token -- [see this doc for details](https://github.com/cesmii/API/blob/main/Docs/jwt.md).

## About the UA Client

A simple OPCUA sample client to demonstrate how to use the [node-opcua](https://github.com/node-opcua/node-opcua) SDK and send data to the SMIP via GraphQL.

* clone the repo
* enter the directory
* run `npm install`
* modify the UA server section of `ua-to-graphql.js` to point to your UA server and desired tag (node)
* run `node ua-to-graphql.js`

Note: This project was forked from https://github.com/node-opcua/node-opcua-sample -- which apparently has an old version of lodash with some security vulnerabilities. If you intend to use in production, you may wish to update the upstream repo, or try out other UA SDKs.

## More information 

The book [NodeOPCUA by example](https://leanpub.com/node-opcuabyexample) provides a comprehensive set of example that goes beyond the simple example provided here.

The [GraphQL website](https://graphql.org/) has more information on the standard. This repo has documentation on the schema used in the CESMII SMIP.
