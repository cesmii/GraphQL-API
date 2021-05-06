# CESMII Smart Manufacturing Innovation Platform
CESMII's Smart Manufacturing Innovation Platform™ (or SMIP™, for short) is a collection of technologies for simplifying access to manufacturing data by normalizing across protocols, enforcing a re-usable object model, and guaranteeing an interface contract for application development. These goals are implemented through the related [Smart Manufacturing Profile™](https://github.com/cesmii/SMProfiles) (SM Profile™) project, a cooperation between OPC UA and CESMII Members, to create re-distributable and extensible Information Model that includes protocol bindings. 

Once applied by an adopting platform (such as the SMIP, or other commercial offerings) the developer interface to the object model is exposed through GraphQL. These documents describe this interface, and how to build raw payloads. Efforts to develop SDKs that provide a simplified adoption path fromspecific programming languages or environments are also discussed.

## GraphQL API
* [Intro to GraphQL](intro.md)
* [GraphQL applied to Smart Manufacturing](graphql-and-manufacturing.md)
* [SMIP GraphQL Endpoint](smip-graphql.md)

### Security and Authentication
* [Acquiring a JSON Web Token (JWT)](jwt.md)

### Queries
* [Type (SM Profile) list](queries.md#query-types)
* [Equipment list](queries.md#query-equipment)
* [Location list](queries.md#query-locations)
* [Attribute list](queries.md#query-attributes)
* [Time Series Values](queries.md#query-timeseries)

### Mutations
* [Inserting or updating time series samples](mutations.md#time-series)
* [Creating a new tag](mutations.md#create-tag)