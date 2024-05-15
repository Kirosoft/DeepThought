import json
import logging
import urllib3
import requests

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

### Test Auth ####
headers = {
    'Content-Type': 'application/json',
    'x-user-id': '12345',
    'x-password': 'my_password'
    }

url = "http://localhost:7071/api/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Test Agent Execution ####

url = "http://localhost:7071/api/flows"
new_flow = {"name":"test_flow","last_node_id":2,"last_link_id":1,"nodes":[{"id":2,"type":"agents/Basic","pos":{"0":564,"1":292,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},"size":{"0":210,"1":106},"flags":{},"order":1,"mode":0,"inputs":[{"name":"Input Request","type":"text","link":1}],"outputs":[{"name":"Answer","type":"text","links":None}],"title":"Agent","properties":{"flows":"ukho"},"widgets_values":[0.5,"default","multiline"]},{"id":1,"type":"agents/UserInput","pos":{"0":212,"1":258,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},"size":{"0":210,"1":58},"flags":{},"order":0,"mode":0,"inputs":[],"outputs":[{"name":"UserText","type":"text","links":[1],"slot_index":0}],"title":"Agent","properties":{"output":"multiline"},"widgets_values":["multiline"]}],"links":[[1,1,0,2,0,"text"]],"groups":[],"config":{},"extra":{},"version":0.4}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

params = {'id': new_flow["name"]}

# create a new user flows
payload = json.dumps(new_flow, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

# get the new flows
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

# delete the new flows
response = requests.delete(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# get the  flows (should be blank)
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# get the  all the flowss
response = requests.get(url, headers=headers)
response_json = response.json()
print(response_json)



