import json



intentdata = [
	{
	"service":[
	{
		"name":"CONNECT",
		"args":"EPS"
	},
	{
		"name":"DISCONNECT",
		"args":"EPS"
	},
	{
		"name":"VLAN",
		"args":"INTEGER"
	},
	{
		"name":"CONDITION",
		"args":"bwnolimit"
	},
	{
		"name":"CONDITION",
		"args":"isolation"
	},
	{
		"name":"CONDITION",
		"args":"unfriendly"
	},
	{
		"name": "schedule_start",
		"start" : "VALUE",
		"duration" :"VALUE"
	},
	{
		"name": "schedule_duration",
		"start" : "VALUE",
		"stop" : "VALUE"
	},
	{
		"name": "schedule_deadline",
		"deadline" : "VALUE",
		"duration" : "VALUE"
	}
	]
	
}

]

with open('indiservicestest.json','w') as outfile:
	json.dump(intentdata,outfile)
