#!/usr/bin/python2.7

################################################################
# @Bevywise.com IOT Initiative. All rights reserved 
# www.bevywise.com Email - support@bevywise.com
#
# custom_auth.py
# 
# The Custom auth hook can be enabled in the broker.conf 
# inside conf/ folder.
# 
# The parameter data will be in dict format and the keys are 'sender','username', 'password', 'clientid', 'ipaddress'
#
################################################################
import requests

# Request Retries Count 
requests.adapters.DEFAULT_RETRIES = 3

# Request URL
url = "https://www.bevywise.com/Auth"

# Request Timeout 
request_timeout = 0.1

# Request Method
request_auth_method = "POST"
# POST | GET | PUT

def handle_Device_Auth(username,password,clientid,ipaddress):
	#print("http request",username,password,clientid,ipaddress)
	try:
		payload = {'password': password,'clientid': clientid,'ipaddress': ipaddress}		
		headers = {
		   	'Content-Type': "application/x-www-form-urlencoded",
		    }
		response = requests.request(request_auth_method,url,data=payload,headers=headers,timeout=request_timeout)
		#print(response,response.status_code)
		if response.status_code == 200:
			print("client "+clientid+"Auth Response Status...  ",end='')
			print('\033[1m'+'\033[92m'+response.status_code+"OK"+ '\033[0m')
			return True
		else:
			print(clientid,"Error Code - ",response.status_code) 
			return False
	except Exception as e:
		print("Error Status -  Max retries exceeded with ",url)
		return False
	