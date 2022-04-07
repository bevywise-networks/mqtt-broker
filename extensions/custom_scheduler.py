###############################################################
#
# @copyright  Bevywise Networks Inc. info@bevywise.com  
# Initial Author - Mahesh Kumar S
#
# The  Custom Sheduler will help you create  your own schedule in
# MQTTRoute by adding your own code on the server side. 
# 
# Data Connectors
# SQL connector will be provided as cursor global variable 
# for querying the Database & Elastic Search connector for 
# querying Elastic if you have enabled custom storage option
#

###############################################################


def schedule_conf():

# ENABLE/DISABLE YOUR SCHEDULE 
#Add your schedule time in MINUTES in 'OnceIn'
#Add your method to call on schedule in 'methodtocall'

	schedules={}

	schedules={
	"STATUS" : "DISABLE",
	'SCHEDULE':'DISABLE',
	'SCHEDULES':[
	{'OnceIn':1,'methodtocall':oneminschedule},
	{'OnceIn':5,'methodtocall':fiveminschedule}]}
	
	return schedules

#
# SQL Connector. It will be sqlite / mssql / mysql cursor based 
# on your configuration in db.conf
# Please construct your queries accordingly. 
global db_cursor

#
#Client object. It used to send/publish message to any active clients
#Simply call the function with parameters like User_name,Client_id,Topic_name,Message,QOS,
global Client_obj

from datetime import datetime


import time
#
# elasstic_search cursor. 
#
global elastic_search
from elasticsearch import Elasticsearch
elastic_search = Elasticsearch("localhost", port = 9200, max_retries = 0)
import json, sys, os
# Called on the initial call to set the SQL Connector

global web_socket
# Web_socket 
def setsqlconnector(conf):
    global db_cursor
    db_cursor=conf["sql"]

def setelasticconnector(conf):
    global elastic_search
    elastic_search=conf["elastic"]

def setwebsocketport(conf):
    global web_socket
    web_socket=conf["websocket"]

def setclientobj(obj):
	global Client_obj
	Client_obj=obj['Client_obj']

def fiveminschedule():
	print("fiveminschedule")
	pass
	#Write your code here
	#print "extension print"

def oneminschedule():
	print("oneminschedule")
	global web_socket
	query = {
			"size" : 0,
			"aggs": {
				"device": {
					"terms": {
						"field": "sender"
					}
				}
			}
		}

	try :
		es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)

		for i in es_data["aggregations"]["device"]["buckets"] :
			device = i["key"]
			query = {
						"query":{
							"bool":{
								"must":[
									{
										"term":{
											"sender": device
										}
									}
								]
							}
						},
						# "query" : {
						# 	"must" [
						# 		{
						# 			"match" : {
						# 				"sender.keyword" : i["key"]
						# 			}
						# 		}
						# 	]
						# },
						"size" : 0,
						"aggs": {
							"device": {
								"terms": {
									"field": "topic"
								}
							}
						}
					}
			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
			for j in es_data["aggregations"]["device"]["buckets"] :

				topic = j["key"]

				query = {
						"size" : 1,
						"query":{
							"bool":{
								"must":[
									{
										"term":{
											"sender": device
										}
									},
									{
										"term":{
											"topic": topic
										}
									}
								]
							}
						}
					}
			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
			for k in es_data["hits"]["hits"] :
				if "message-integer" in k["_source"] :
					key_list = ["message-integer"]
				elif "message-float" in k["_source"] :
					key_list = ["message-float"]

				elif "message-dict" in k["_source"] :
					key_list = getJsonKeys(k["_source"]["message-dict"], "", [])
			aggs = aggQueryBuilder(key_list)
			query = {
								"size": 0,
								"query":{
									"bool":{
										"must":[
											{
												"term":{
													"sender": device
												}
											},
											{
												"term":{
													"topic": topic
												}
											},
											{
												"range": {
													"unixtime": {
														"gte": time.time() - (5* 60), 
														"lte": time.time()                  
													}
												}
											}
										]
									}
									# "range": {
									# 	"timestamp": {
									# 		"gte": "now-5m", 
									# 		"lte": "now"                  
									# 	}
									# }
								},
								"aggs": aggs
									# {
									# "avg": {
									# 	"avg": {
									# 		"field": "message-integer"
									# 	}
									# },
									# "min": {
									# 	"min": {
									# 		"field": "message-integer"
									# 	}
									# },
									# # "value_count": {
									# # 	"value_count": {
									# # 		"field": "message-dict.Param1"
									# # 	}
									# # },
									# # "avg_corrected_param_3": {
									# # 	"avg": {
									# # 		"field": "message-dict.Param3"
									# # 	}
									# # },
									# "max": {
									# 	"max": {
									# 		"field": "message-integer"
									# 	}
									# }
								# }
							}
			# print(json.dumps(query))
			# print(query)
			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
			# print(json.dumps(es_data["aggregations"]))




			es_payload = {}
			es_payload["data"] = {}
			for d in es_data["aggregations"] :
				if not es_data["aggregations"][d] == None :
					es_payload["data"][d] = es_data["aggregations"][d]["value"]

			es_payload["device"] = device
			es_payload["topic"] = topic

			es_payload["timestamp"] = datetime.now()
			es_payload["unixtime"] = int(time.time() * 1000)

			elastic_search.index(index="bevywise-agg", doc_type = "5-min", body = es_payload)



			data = { "work" : "agg", "id" : device, "topic" : topic, "msg" : json.dumps(es_payload["data"]), "time" : es_payload["unixtime"] }
			# data = '{ "work" : "recv_pub",  "name" : "'+str(username)+'", "id" : "'+str(clientid)+'", "topic" : "'+str(topic_name)+'", "msg" : "'+str(message)+'", "qos" : "'+str(qos)+'", "retain" : "'+str(retain)+'", "packet" : "'+str(packetid)+'","status" : "'+str(status)+'", "time" : "'+str(time_stamp)+'" }'
			web_socket.send_message_to_all(json.dumps(data).encode('utf-8'))
			# print(json.dumps(es_data))
	except Exception as e :
		print(e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
def getJsonKeys(msg, init_key, key_list) :
    for i in msg :
        if type(msg[i]) == dict :
            init_key = init_key + "." + i
            getJsonKeys(msg[i], init_key, key_list)
            for k in i :
                init_key = init_key[:-1]
            init_key = init_key[:-1]
        elif type(msg[i]) == int or type(msg[i]) == float :
            init_key = init_key + "." + i
        else :
            init_key = init_key + "." + i
        if init_key != "" and type(msg[i]) != dict :
            key_list.append(init_key[1:])
            for k in i :
                init_key = init_key[:-1]
            init_key = init_key[:-1]
    return key_list

def aggQueryBuilder(key_list) :
	aggs = {}

	pre_key = ""
	if not(key_list[0] == "message-integer") and not(key_list[0] == "message-float") :
		pre_key = "message-dict."
	for i in key_list :
	 	aggs[i] = {"avg": {"field" : pre_key + i}}

	 	# aggs[i + "-max"] = {"max": {"field" : pre_key + i}}

	 	# aggs[i + "-min"] = {"min": {"field" : pre_key + i}}
	return aggs