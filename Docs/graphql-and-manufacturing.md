# Reliable Structures
The Smart Manufacturing Innovation Platform™ (SMIP™) is a strongly-typed development environment for manufacturing data. Combined with the Smart Manufacturing Profile™ (SM Profile™), CESMII and the OPC Foundation are working to create distributable Information Models (also known as Class or Type definitions) for common manufacturing equipment and processes that can be easily bound to real-world data source through adaptation to a variety of protocols.

GraphQL objects are expressed as Javascript Object Notation (JSON) payloads, that can de-serialized into a programming language or environment of choice as strongly-typed objects. The structure of these objects can be derived from a GraphQL payload, or identified in advanced through SM Profile which, at this level, functions as an Interface Description Language.

While there's only one pre-release version of the SMIP and SM Profiles currently, we envision that both the Profiles and the Interface will have revisions over time. To ensure existing applications remain compatible, version information will be contained in each SM Profile and in the API response.

GraphQL is well-suited to representing complex Graph relationships, such as the ones stored in a SMIP instances, or in an OPC UA Server, because it allows a developer to specify exactly what objects, and what relationships they are interested in. Read below for information about queries and expected responses. CESMII has combined GraphQL with a JSON Web Token (JWT) approach for application security. The article [Acquiring a JSON Web Token](jwt.md) provides more detail about the security model.

Unlike REST, GraphQL uses a single endpoint URL for all queries. To make the interface discoverable, the specification includes a standard schema query so that there's a common way to learn about the endpoint's capabilities. See the page [SMIP GraphQL Endpoints](smip-graphql.md) for more details.

## Definable Queries
This section is a stub

## Predictable Results
This section is a stub