# Intro to GraphQL

> GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data. GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time, and enables powerful developer tools.

_- Excerpt from GraphQL.org_

GraphQL was developed by Facebook as a way to improve on REST-style interfaces that frequently returned too much or too little data for a particular query. REST's inefficiency stems from the fact that the interface developer can't know in advance exactly what payloads an external developer may need access to. The result is payloads that either return too much data, which needs to be scraped and parse for the needed information, or not enough data, resulting in multiple repeated calls to "drill in" to what was needed.

GraphQL solves these problems, while retaining many of the advantages of REST, like easy-to-parse JSON responses, and easy-to-invoke HTTP/S endpoints.

Beyond just improving efficiency, Facebook needed a way to programmatically understand non-hierarchical relationships between nodes on their network (users, topics, locations, etc...). A Graph database can represent many different relationship types, but existing APIs weren't well suited to this complexity. In manufacturing, we also have relationships between nodes. We're often used to thinking about a ISA-95 style hierarchy, but that structure is not sufficient for representing network topology, physics interactions between equipment, or material flow (to name a few other links in the graph.) Fortunately, Facebook published GraphQL publically in 2015, where its been adopted by company's like Microsoft, Intuit, AirBnB, and Coursera.

You can read more about GraphQL, or [download the spec](http://spec.graphql.org/) at [GraphQL.org](https://graphql.org/).
To learn how CESMII is applying GraphQL, read the article [GraphQL applied to Smart Manufacturing](smip-graphql.md).