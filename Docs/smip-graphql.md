# SMIP GraphQL Endpoint

In GraphQL, the endpoint is always the same, but the query payload changes to indicate the response payload you wish to retrieve. Currently, GraphQL is an optional features of the SMIP -- if the endpoint is not available on your instance of the SMIP, please contact CESMII with your base URL and request activation.

## Locating the Endpoint

The GraphQL endpoint is available as a URI based on your SMIP instance domain, eg:

`https://[yoursmip.cesmii.net]/graphql`

You can send queries to your SMIP instance with a REST client, or virtually any tool capable of making an HTTPS call.

## Exploring the Endpoint

Once GraphQL is activated on your SMIP instance, you'll also have a basic web UI, called GraphiQL, for exploring the endpoint, deployed at another URI based on your SMIP instance domain, eg:

`https://[yoursmip.cesmii.net]/graphiql`

From this UI, you can discover the schema of the endpoint, build and make queries against it, and previous responses, all from your web browser. Any query that you can build and post from GraphiQL can be used in any other programming language or development tool that supports HTTP Post and JSON parsing. Some example queries can be found on the page [GraphQL Queries](queries.md).

## Authorized Endpoint Access

Now that you know where your endpoint is, you'll need an authorization token to send queries to it. Read about [acquiring a token here](jwt.md).