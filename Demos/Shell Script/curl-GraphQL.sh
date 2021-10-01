#!/bin/bash

url='https://demo.cesmii.net/graphql'
# Fill the information below from https://demo.cesmii.net/developer/graphql-authenticator
role=""
userName=""
authvalue=""
passwd=""


queryauth1='{"query":"mutation {authenticationRequest(input: {authenticator: \"'
queryauth2="$authvalue\\\", role: \\\"$role\\\", userName: \\\"$userName\\\"}) { jwtRequest { challenge message }  }}\"}"


echo "Getting the Challenge Response from ${url} "
echo

res=`curl ${url} -H 'Content-Type: application/json'  --data-binary "${queryauth1}${queryauth2}"`

challenge=`echo $res | cut -d":" -f5  | cut -d\" -f2`
echo
echo "Challenge Response from ${url} is $challenge "
echo

echo $res | python -m json.tool

querytok1='{"query":"mutation {authenticationValidation(input: {authenticator: \"'
querytok2="$authvalue\\\", signedChallenge: \\\"$challenge|$passwd\\\"} ){ jwtClaim  }}\"}"

token=`curl ${url} -H 'Content-Type: application/json'  --data-binary "${querytok1}${querytok2}"`

bearer_token=`echo $token | cut -d":" -f4 | cut -d\" -f2`

echo $token | python -m json.tool

query='{"query":"{ equipments { displayName, id }   }"}'
echo
echo "Bearer Token from $url is $bearer_token \n"
echo

echo "Query result from ${url} for the $query is "
echo


response=$(curl ${url} -H 'Content-Type: application/json' -H "Authorization: Bearer ${bearer_token}" --data-binary "${query}")

echo $response | python -m json.tool
