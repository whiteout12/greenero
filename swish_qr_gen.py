import requests
import json
from json import dumps
import base64

def swishQR(payee, amount, message):
	#print(payee)
	#print(amount)
	#print(message)
	url = "https://mpc.getswish.net/qrg-swish/api/v1/prefilled"
	#data = {”format”:”png”,”size”:300,”message”:{”value”:”test message”,”editable”:false},”amount”:{”value”:100,”editable”:false}}
	data = {'format':'svg','size':300,'message':{'value':message,'editable':'false'},'amount':{'value':amount,'editable':'false'}, 'payee':{'value':payee,'editable':'false'}}
	headers = {'Content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	print(r.content)
	#file = open("sample_image.png", "wb")
	file = open("static/swish_qr.svg", "wb")
	file.write(r.content)
	file.close()

	return file

def swishQRbase64(payee, amount, message):
	#print(payee)
	#print(amount)
	#print(message)
	url = "https://mpc.getswish.net/qrg-swish/api/v1/prefilled"
	data = {'format':'svg','size':300,'message':{'value':message,'editable':'false'},'amount':{'value':amount,'editable':'false'}, 'payee':{'value':payee,'editable':'false'}}
	headers = {'Content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	print(r.status_code)
	if r.status_code == 200:
		return base64.b64encode(r.content).decode("utf-8")
	else:
		return None