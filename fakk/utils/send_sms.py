import requests
from fakk import app

def sendSMS(phone, message):

	username = app.config['CELLSYNT_USERNAME']
	password = app.config['CELLSYNT_PASSWORD']
	destination ='0046'+ phone[1:len(phone)]
	text = message
	#charset = 'ISO-8859-1'
	charset = 'UTF-8'
	originatortype = 'alpha'
	originator = 'fakk.'
	sms_type = ''
	flash = ''
	#print(destination)
	#print(username + password + destination + message)

	url = 'https://se-1.cellsynt.net/sms.php?username='+username+'&password='+password+'&destination='+destination+'&type=text&charset='+charset+'&text='+text+'&originatortype='+originatortype+'&originator='+originator+''
	#print(url)
	#data = {'format':'svg','size':300,'message':{'value':message,'editable':'false'},'amount':{'value':amount,'editable':'false'}, 'payee':{'value':payee,'editable':'false'}}
	#headers = {'Content-type': 'application/json'}
	
	#rold = requests.post(url, data=json.dumps(data), headers=headers)
	r = requests.get(url)
	
	#print(r.status_code)
	
	return 'None'