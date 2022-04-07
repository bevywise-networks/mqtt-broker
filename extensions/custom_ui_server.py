###############################################################
#
# @copyright  Bevywise Networks Inc. info@bevywise.com  
# Initial Author - Mahesh Kumar S
#
# The UI custom server will help you customize the UI of the 
# MQTTRoute by adding your own code on the server side. 
# 
# Data Connectors
# SQL connector will be provided as cursor global variable 
# for querying the Database & Elastic Search connector for 
# querying Elastic if you have enabled custom storage option
#
# New URL Addition 
# Add your new functionality using the URL and the corresponding 
# method.  These URLs can be invoked from your User Interface 
# for manipulating data. We support GET http method in 
# this version. 
#
###############################################################

#
# SQL Connector. It will be sqlite / mssql / mysql cursor based 
# on your configuration in db.conf
# Please construct your queries accordingly. 
#
import sys
global db_cursor
#username','client_send_api','topic_name','message',1,0,'10',0


# elasstic_search cursor. 

global elastic_search


from datetime import datetime

import json

import ast
import time
try :
    from elasticsearch import Elasticsearch

    elastic_search = Elasticsearch(host="localhost", port=9200)
except Exception as e :
    print(e)
import os, sys

#
#Client object. It used to send/publish message to any active clients
#Simply call the function with parameters like User_name,Client_id,Topic_name,Message,QOS,
global Client_obj

# Called on the initial call to set the SQL Connector
def setsqlconnector(conf):

    global db_cursor
    db_cursor=conf["sql"]


# Called on the initial call to set the Elastic Search Connector

def setelasticconnector(conf):
    global elastic_search
    elastic_search=conf["elastic"]

def setclientobj(obj):
    global Client_obj
    Client_obj=obj['Client_obj']



#
# Configure your additional URLs here. 
# The default URLs are currently used for the UI. 
# Please don't remove them, if you are building it over the same UI. 
#

def custom_urls():

    urllist={
        "AUTHENTICATION":'DISABLE',
        "URL_REDIRECT": "/",
        "urls":[
        {"/dashboard/" : dashboard},
        {"/bwiot/extend-ui/create-dashboard/":create_dashboard},
        {"/bwiot/extend-ui/get-dashboard/":get_dashboard},
        {"/bwiot/extend-ui/delete-dashboard/":delete_dashboard},
        {"/bwiot/extend-ui/widget/" : get_widgets},
        {"/bwiot/extend-ui/create-widget/" : create_widget},
        {"/bwiot/extend-ui/delete-widget/" : delete_widget}
        ]
    }
    return urllist

# write your url function codes in the following methods
def method(data):
    return ("BEVYWISE NETWORKS")

def method1(data):
    return("BEVYWISE NETWORKS")

def method2(data):
    return("BEVYWISE NETWORKS")
    






def dashboard(data) :
    print("JMNJKHJKJ")
    return("extend_ui.html")

def create_dashboard(data) :
    try :
        print(data)
        es_data = data
        response = data
        es_data["timestamp"] = datetime.now()
        es_data["unixtime"] = int(time.time())
        es = elastic_search.index(index="dashboard", doc_type = "dashboard", id =int(response["unixtime"]), body = es_data)
        response["id"] = es["_id"]
        del response["timestamp"]
        response["status"] = "Success"
    except Exception as e :
        print(e)
        response = {"status" : "Failed"}
    finally :
        print(response)
        return response

def get_dashboard(data) :
    try:
        response = {}
        response["dashboards"] = []
        print(data)
        es = elastic_search.search(index="dashboard", doc_type = "dashboard", body = {"query":{"bool" : {"must" :[]}}})

        for i in es["hits"]["hits"] :
            response["dashboards"].append({"name" : i["_source"]["name"], "id" : i["_id"], "description" : i["_source"]["desc"], "time" : i["_source"]["unixtime"]})
    except Exception as e:
        response["status"] = "Failed"
    else:
        response["status"] = "Success"
    finally:
        return response



def delete_dashboard(data) :
    try:
        print(data)
    except Exception as e:
        raise
    else:
        pass
    finally:
        pass

def get_widgets(data) :
    try:
        # print(data)
        response = {}
        es = elastic_search.search(index="widget", doc_type="widget", body={"query":{"bool":{"must":[{"term":{"id.keyword":data["id"]}}]}}})
        # print(es)
        # dbnew.execute("SELECT type, name, device, topic, data, id, `key` FROM widget WHERE dashboard_id = %d" %(int(dashboard_id)))
        # mysql_data = dbnew.fetchall()
        response = {}
        datum = {}
        widget_init = []
        widget_position = {}
        widget_extra = {}
        widgetData = {}
        widgets_id_list = {}
        l = 0
        for i in es["hits"]["hits"] :

            w_id = i["_id"]
            i = i["_source"]
            widget_init.append({"type" : i["type"], "name" : i["name"], "device" : i["device"], "topic" : i["topic"], "id" : w_id, "key" : i["key"], "widget_id" : "widget_" + str(l)})
            widgets_id_list.setdefault(i["type"], {}).setdefault(i["device"], {}).setdefault(i["topic"], {}).setdefault(i["key"], []).append("widget_" + str(l))
            widget_extra["widget_" + str(l)] = i["data"]
            datum.setdefault(i["device"], {}).setdefault(i["topic"], get_data(i["device"], i["topic"]))
            widgetData.setdefault(i["type"], {}).setdefault(i["device"], {}).setdefault(i["topic"], []).append(i["key"])
            widget_position["widget_" + str(l)] = {"id" : w_id, "name" : i["name"]}
            l += 1
            # data["widgets"].append({"id" : i[0], "name" : i[1], "time" : i[3]})
        response["status"] = "Success"
        response["widget_id"] = widgets_id_list
        response["widget_extra"] = widget_extra
        response["widget_position"] = widget_position
        response["widgets"] = widgetData
        response["data"] = datum
        response["init"] = widget_init
    except Exception as e:
        print(e)


        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        response["status"] = "Failed"
    else:
        response["status"] = "Success"
    finally:
        return response


def get_data(device, topic) :
    try :
        es = elastic_search.search(index="bevywise-agg", doc_type="5-min", body={"query" : {"bool" : {"must":[{"match":{"device.keyword": device}},{"match":{"topic.keyword": topic}}]}}})

        datum = []
        for i in es["hits"]["hits"] :
            data = {}
            if "message-integer" in i["_source"]["data"] :
                data["message"] = i["_source"]["data"]["message-integer"]
            elif "mesage-float" in i["_source"]["data"] :
                data["message"] = i["_source"]["data"]["message-float"]
            else :
                data["message"] = {}
                data["message"]= i["_source"]["data"]
                # data["message"] = i["_source"]["data"]
            data["time"] = i["_source"]["unixtime"]

            datum.append(data)
        # print(data)
        return datum
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

def create_widget(data) :
    try:
        print(data, type(data))
        response = {}
        data["data"] = ast.literal_eval(data["data"])
        # data = json.loads(json.dumps(data))
        es = elastic_search.index(index="widget", doc_type="widget", body=data)
        print(es)
    except Exception as e:
        print(e)
        response["status"] = "Failed"
    else:
        response["status"] = "Success"
    finally:
        return response
        

def delete_widget(data) :
    try:
        pass
    except Exception as e:
        raise
    else:
        pass
    finally:
        pass