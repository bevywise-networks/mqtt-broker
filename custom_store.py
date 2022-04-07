#!/usr/bin/python2.7

################################################################
# @Bevywise.com IOT Initiative. All rights reserved 
# www.bevywise.com Email - support@bevywise.com
#
# custom_store.py
#
# The custom data store hook for the Big Data Storage. 
# The Custom data hook can be enabled in the broker.conf 
# inside conf/ folder.
# 
# The parameter data will be in dict format and the keys are 'sender','topic', 'message', 'unixtime', 'timestamp'
#
################################################################


#
# SQL Connector. It will be sqlite / mssql / mysql cursor based 
# on your configuration in db.conf
# Please construct your queries accordingly. 
#
global db_cursor

#
# elasstic_search cursor. 
#
global elastic_search

from elasticsearch import Elasticsearch
from elasticsearch import helpers
elastic_search = Elasticsearch("localhost", port = 9200, max_retries = 0)

from datetime import datetime
import json
import ast
import os, sys

#
#Client object. It used to send/publish message to any active clients
#Simply call the function with parameters like User_name,Client_id,Topic_name,Message,QOS,

global Client_obj

sys.path.append(os.getcwd()+'/../extensions')

# Called on the initial call to set the SQL Connector

def setsqlconnector(conf):

    global db_cursor
    db_cursor=conf["sql"]
# Called on the initial call to set the Elastic Search Connector

def setelasticconnector(conf):
	global elastic_search
	elastic_search=conf["elastic"]

	try :
		if not elastic_search.indices.exists(index="bevywise"):
			mapping = 	{
							"settings": {
								"number_of_shards": 1
							},
							"mappings": {
								"mappings" : {
									"properties": {
										"sender": { "type": "keyword" },  
										"topic": { "type": "keyword"  }, 
										"message-dict": { "type": "object"},
										"message-integer" : {"type" : "integer"},
										"message-float" : {"type" : "float"},
										"message-string" : {"type" : "text"},
										# "timestamp" : {"type" : "date", "format": "dd-MM-yyyy HH:mm:ss"}
									}
								}
							}
						}
			elastic_search.indices.create(index = "bevywise", body=mapping)
	except Exception as e:
		print(e)
global datasend
def setwebsocketport(conf):
    global web_socket
    web_socket=conf["websocket"]

def setclientobj(obj):
	global Client_obj
	Client_obj=obj['Client_obj']
	#Client_obj('Mahesh','clientno1','test','jsvkvlkdsvbkvcksdhvcksdvcsdkjvcs',1)

# Importing the custom class into the handler

from customimpl import DataReceiver

datasend = DataReceiver()

def handle_Received_Payload(data):

	#
	# Write your code here. Use your connection object to 
	# Send data to your data store

	# print("print in the handle_received_payload",data)

	# result = datasend.receive_data(data)

	es_msg_type = {int : "message-integer", float : "message-float", str : "message-string", dict : "message-dict", list : "message-dict"}
	try :
		es_msg = ast.literal_eval(data["message"])
	except Exception as e :
		data["message"] = (data["message"]).replace('["0"]]', '[]')
		try :
			# print(data["message"])
			es_msg = ast.literal_eval(data["message"])
		except Exception as e :
			# print(e, "#################", data["message"])
			es_msg_type = "message-string"
			es_msg = data["message"]
	try :
		data[es_msg_type[type(es_msg)]] = es_msg
		del data["message"]
		# date_time = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
		# print(date_time, type(date_time))
		# data["timestamp"] = date_time
		# print(data, data["message-dict"]["bid"], type(data["message-dict"]["bid"]))

		data["timestamp"] = datetime.now()
		elastic_search.index(index= "bevywise", doc_type = 'recv_payload', body = data)
	except Exception as e :
		print(e, 97)
	# if result is none then write failed
def handle_Sent_Payload(data):

	pass

	#
	# Write your code here. Use your connection object to 
	# Send data to your data store

	# print("print in the handle_Sent_payload",data)

	# result = datasend.sent_data(data)




# def agg() :
# 	query = {
# 			"size" : 0,
# 			"aggs": {
# 				"device": {
# 					"terms": {
# 						"field": "sender"
# 					}
# 				}
# 			}
# 		}

# 	try :
# 		es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)

# 		for i in es_data["aggregations"]["device"]["buckets"] :
# 			device = i["key"]
# 			query = {
# 						"query":{
# 							"bool":{
# 								"must":[
# 									{
# 										"term":{
# 											"sender": device
# 										}
# 									}
# 								]
# 							}
# 						},
# 						# "query" : {
# 						# 	"must" [
# 						# 		{
# 						# 			"match" : {
# 						# 				"sender.keyword" : i["key"]
# 						# 			}
# 						# 		}
# 						# 	]
# 						# },
# 						"size" : 0,
# 						"aggs": {
# 							"device": {
# 								"terms": {
# 									"field": "topic"
# 								}
# 							}
# 						}
# 					}
# 			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
# 			for j in es_data["aggregations"]["device"]["buckets"] :

# 				topic = j["key"]

# 				query = {
# 						"size" : 1,
# 						"query":{
# 							"bool":{
# 								"must":[
# 									{
# 										"term":{
# 											"sender": device
# 										}
# 									},
# 									{
# 										"term":{
# 											"topic": topic
# 										}
# 									}
# 								]
# 							}
# 						}
# 					}
# 			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
# 			for k in es_data["hits"]["hits"] :
# 				if "message-integer" in k["_source"] :
# 					key_list = ["message-integer"]
# 				elif "message-float" in k["_source"] :
# 					key_list = ["message-float"]

# 				elif "message-dict" in k["_source"] :
# 					key_list = getJsonKeys(k["_source"]["message-dict"], "", [])
# 			aggs = aggQueryBuilder(key_list)
# 			query = {
# 								"size": 0,
# 								"query":{
# 									"bool":{
# 										"must":[
# 											{
# 												"term":{
# 													"sender": device
# 												}
# 											},
# 											{
# 												"term":{
# 													"topic": topic
# 												}
# 											}
# 										]
# 									}
# 								},
# 								"aggs": aggs
# 									# {
# 									# "avg": {
# 									# 	"avg": {
# 									# 		"field": "message-integer"
# 									# 	}
# 									# },
# 									# "min": {
# 									# 	"min": {
# 									# 		"field": "message-integer"
# 									# 	}
# 									# },
# 									# # "value_count": {
# 									# # 	"value_count": {
# 									# # 		"field": "message-dict.Param1"
# 									# # 	}
# 									# # },
# 									# # "avg_corrected_param_3": {
# 									# # 	"avg": {
# 									# # 		"field": "message-dict.Param3"
# 									# # 	}
# 									# # },
# 									# "max": {
# 									# 	"max": {
# 									# 		"field": "message-integer"
# 									# 	}
# 									# }
# 								# }
# 							}
# 			# print(json.dumps(query))
# 			es_data = elastic_search.search(index = "bevywise", doc_type = "recv_payload", body=query)
# 			print(json.dumps(es_data["aggregations"]))
# 			# print(json.dumps(es_data))
# 	except Exception as e :
# 		print(e)
# 		exc_type, exc_obj, exc_tb = sys.exc_info()
# 		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
# 		print(exc_type, fname, exc_tb.tb_lineno)
# def getJsonKeys(msg, init_key, key_list) :
#     for i in msg :
#         if type(msg[i]) == dict :
#             init_key = init_key + "." + i
#             getJsonKeys(msg[i], init_key, key_list)
#             for k in i :
#                 init_key = init_key[:-1]
#             init_key = init_key[:-1]
#         elif type(msg[i]) == int or type(msg[i]) == float :
#             init_key = init_key + "." + i
#         else :
#             init_key = init_key + "." + i
#         if init_key != "" and type(msg[i]) != dict :
#             key_list.append(init_key[1:])
#             for k in i :
#                 init_key = init_key[:-1]
#             init_key = init_key[:-1]
#     return key_list

# def aggQueryBuilder(key_list) :
# 	aggs = {}

# 	pre_key = ""
# 	if not(key_list[0] == "message-integer") and not(key_list[0] == "message-float") :
# 		pre_key = "message-dict."
# 	for i in key_list :
# 	 	aggs[i + "-avg"] = {"avg": {"field" : pre_key + i}}

# 	 	aggs[i + "-max"] = {"max": {"field" : pre_key + i}}

# 	 	aggs[i + "-min"] = {"min": {"field" : pre_key + i}}
# 	return aggs
# schedule.every(5).seconds.do(agg)
