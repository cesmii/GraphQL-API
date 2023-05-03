# SMIP Queries

In GraphQL, the endpoint is always the same, but the query payload changes to indicate the response payload you wish to retrieve. For more information on accessing the GraphQL endpoint for your SMIP instance, see the page [SMIP GraphQL Endpoint](smip-graphql.md).

## Example Queries

### Querying Equipment Types (SM Profiles)

The following query payload returns a list of Equipment Types (also known as SM Profiles) in a given SMIP instance:

```
query EquipmentTypesQuery {
  equipmentTypes {
    id
    displayName
    relativeName
  }
}
```

We can expand this query to ask it to also return a list of the Equipment (instance object) of each Equipment Type (SM Profile):

```
query EquipmentTypesAndInstancesQuery {
  equipments {
    displayName
    id
      equipmentType {
      displayName
    }
  }
}
```

If you only want Equipment Types defined locally, you can query your library for type definitions:

```
query MyLocalEquipmentQuery {
  libraries (condition:{displayName:"Local Library"}) {
    id
    displayName
    asThing {
      thingsByPartOfId(condition: { systemType: "type" }) {
        id
        displayName
        systemType
      }
    }
  }
}
```


### Querying Equipment

The following query payload returns a list of Equipment instances in a given SMIP instance, independent of Type:

```
query EquipmentInstancesQuery { 
    equipments { 
        id,
        displayName
       	relativeName
    }   
}
```

### Querying Locations

The following query payload returns a list of Locations in a given SMIP instance:

```
query placeQuery {  
    places {        
        displayName      
        partOf {        
            displayName      
        }    
    }
}
```

### Querying Attributes

The following query payload returns a list of all Attributes in a given SMIP instance:

```
query AttributeQuery { 
    attributes { 
        displayName, 
        id, 
        partOfId, 
        tagId 
    }  
}
```

### Querying Attributes and their values

The following query payload returns a list of all Attributes and their floatvalue in a given SMIP instance:

```
query AttributeQuery {
    attributes {
        displayName,
        id,
        partOfId,
        tagId
	getTimeSeries(
   	startTime: "2022-01-01 00:00:00+00"
      	endTime: "2022-01-30 00:12:00+00"
      	maxSamples: 1
    	) {
      		floatvalue
      		ts
    	}
    }
}
```
   
This query lists only the Attributes for a given Equipment Type definition:

```
query EquipmentTypeAttributes {
  equipmentTypes(filter: {displayName: {equalTo: "Boiler Drum"}}) {
    id
    displayName
    typeToAttributeTypes {
      id
      displayName
    }
  }
}

```

### Querying Time Series Values

The following query returns a list of Time Series sample values for a given Instance Attribute Tag within the specified time range.

**Note:** to turn off down-sampling, you can set `maxSamples` to 0.

```
query HistoryQuery {
    getRawHistoryDataWithSampling(
            maxSamples: 10, 
            ids: ["1690"], 
            startTime: "2021-02-20 00:00:00+00", 
            endTime: "2021-02-21 00:12:00+00"
    ) {
        id
        floatvalue
        dataType
        ts
    }
}
```

### Querying Relationships Between Equipment

The following query returns a list of relationships the equipment with the ID 5184 has with other equipment

```
query RelationshipQueryBySubjectId {
  relationships(filter: {subjectId: {equalTo: "5184"}}) {
    id
    objectId
    typeName
    relationshipTypeName
    subjectId
    relationshipTypeId
  }
}
```

## Other Operations

With GraphQL, other types of operations can be performed with special queries called Mutations. Some  [Mutation examples can be found here](mutations.md).
