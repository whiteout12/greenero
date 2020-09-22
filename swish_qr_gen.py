import requests
import json
from json import dumps

def swishQR():
	url = "https://mpc.getswish.net/qrg-swish/api/v1/prefilled"
	data = {'format':'svg','size':300,'message':{'value':'test message','editable':'false'},'amount':{'value':110,'editable':'false'}, 'payee':{'value':'0730514019','editable':'false'}}
	headers = {'Content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(data), headers=headers)
	#print(r)
	#file = open("sample_image.png", "wb")
	#file = open("sample_image.svg", "wb")
	#file.write(r.content)
	#file.close()
