global db_cursor
#
# elastic_search cursor
#
global elastic_search
import os, sys
global datasend

custom_store.py
global Client_obj
sys.path.append(os.getcwd()+’/../extensions’)

# Called on the initial call to set the SQL Connector

def setsqlconnector(conf):

global db_cursor
db_cursor=conf[“sql”]
# Called on the initial call to set the Elastic Search Connector

def setelasticconnector(conf):
global elastic_search
elastic_search=conf[“elastic”]
def setwebsocketport(conf):
global web_socket
web_socket=conf[“websocket”]

def setclientobj(obj):
global Client_obj
Client_obj=obj[‘Client_obj’]
#Client_obj
