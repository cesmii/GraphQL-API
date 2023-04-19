# EnergyConsumption Functions

These functions read data from the US Government (EIA) APIs and insert it into the SMIP where it can be used for analysis, calculations or other apps.

Requires a SMIP instance and Auth configuration -- see: [https://github.com/cesmii/API/blob/main/Docs/jwt.md](https://github.com/cesmii/API/blob/main/Docs/jwt.md)

Requires an API key from EIA -- see: [https://www.eia.gov/opendata/](https://www.eia.gov/opendata/)

Requires API credentials from WattTime -- see: [https://www.watttime.org/api-documentation/#introduction](https://www.watttime.org/api-documentation/#introduction)

## Contributions

This was a UCLA intern project, written by Wenjie Liu with support from Jonathan Wise and Sean Coxen, and is provided "as-is" as open source under the enclosed license.

# Setup Environment

## Local

- Copy `local.settings-example.json` to `local.settings.json`
- In local.settings.json, replace YOURINSTANCE with the SMIP instance you are using
- In local.settings.json, replace YOURAPIKEY with the API key you got from EIA

## On SMIP Platform

- Create a big-region equipment type with attributes below (Data Type:float, Data Source:Dynamic). In local.settings.json, replace YOUR_BIG_REGION_EQUIPMENT_TYPE_ID with this equipment type ID.
	+ `demand`
	+ `generation_total`
	+ `generation_coal`
	+ `generation_other`
	+ `generation_hydro`
	+ `generation_nuclear`
	+ `generation_solar`
	+ `generation_wind`
	+ `generation_natural_gas`
	+ `generation_petroleum`

- Create a small-region equipment type with attributes below (Data Type:float, Data Source:Dynamic). In local.settings.json, replace the YOUR_SMALL_REGION_EQUIPMENT_TYPE_ID with this equipment type ID.
	+ `demand`

- Create a state equipment type with attributes below (Data Type:float, Data Source:Dynamic). In local.settings.json, replace YOUR_STATE_EQUIPMENT_TYPE_ID with this equipment type ID.
	+ `production`
	+ `consumption`

- Create a carbon region equipment type with the attributes below (Data Type:string, Data Source:Dynamic). In local.settings.json, replace YOUR_CARBON_EQUIPMENT_TYPE_ID with this equipment type ID.
	+ `measurement`
	+ `balancing_authority`

- Create a Place in the Physical model, such as "USA"

- Create an equipment named as "us_energy" using the state equipment type you just created in the Place you just created. In local.settings.json, replace YOUR_PARENT_EQUIPMENT_ID with the equipment ID of "us_energy".

- Create an authenticator. Then in local.settings.json, replace YOURAUTHID, YOURAUTHSECRET, YOURUSERNAME, YOURAUTHROLE with the information of the authenticator you just created.

## Azure

- Use Configuration to set Application settings as in `local.settings-example.json`
- Insert your appropriate credentials for SMIP and EIA
- When setting Configuration parameters in Azure, ensure each variable name matches with what is shown in local.settings-example.json, eg:
	+ `SmipSettings:GraphQLEndpoint`