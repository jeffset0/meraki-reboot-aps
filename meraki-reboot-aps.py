import json
import sys
import requests
import time
import email
import smtplib
import os
from dotenv import load_dotenv
from pathlib import Path # python3 only

# get API_KEY EMAIL_RECEIVER EMAIL_SENDER EMAIL_SERVER
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

cisco_meraki_api_Key = os.getenv("API_KEY")
organizationId = os.getenv("ORGANIZATION_ID")

baseUrl = 'https://api.meraki.com/api/v0/'
inventory_api_url = "organizations/{}/inventory".format(organizationId)

headers = {
    'X-Cisco-Meraki-API-Key': cisco_meraki_api_Key,
    'Content-Type': 'application/json'
    }

get_inventory = requests.get(baseUrl+inventory_api_url,
                            headers=headers,
                            )

# Parse the get_inventory into json
inventory_json = get_inventory.json()

networkID = ""
serial = ""

# Opens or create a file name results
f = open('results.txt', "w+")

# loop over all the dictionaries inside inventory_json,
# if API is inside the dictionary it will get the NetworkID and the serial and then write it to the string above

for ap in inventory_json:
    try:
        #List of locations to check for
        locations = ('LOCATION1', 'LOCATION2')
        if any(loc in ap['name'] for loc in locations):
            networkID = ap['networkId']
            serial = ap['serial']
            ap_name = ap['name']
            f.write('{0} {1} {2} \n'.format(networdID, serial, ap_name))

            reboot_api_call = requests.post(
                baseUrl+'/networks/{}/devices/{}/reboot'.format(networkID, serial),
                headers=headers)

            if reboot_api_call.status_code == 200:
                print('Rebooting --->', ap_name, '---> Successful\n---------------------------------------------------' , file=f)
            if reboot_api_call.status_code == 400:
                print ('Rebooting --->', ap_name, '---> Bad Request\n---------------------------------------------------' , file=f)
            if reboot_api_call.status_code == 403:
                print ('Rebooting --->', ap_name, '---> Forbidden\n---------------------------------------------------' , file=f)
            if reboot_api_call.status_code == 404:
                print ('Rebooting --->', ap_name, '---> Not Found\n---------------------------------------------------' , file=f)
            if reboot_api_call.status_code == 429:
                print ('Rebooting --->', ap_name, '---> Too Many Requests\n---------------------------------------------------' , file=f)
            time.sleep(1)
    except:
        continue

# closes the file
f.close()

# Setting up the SMTP Server
sender = os.getenv("EMAIL_SENDER")
receiver = os.getenv("EMAIL_RECEIVER")
server = os.getenv("EMAIL_SERVER")
smtp_server = smtplib.SMTP(host=server,port=25)

f = open('results.txt', "r")

# reads the information inside the file results
script_result = f.read()

message = """From: <{}>
To: <{}>
Subject: Meraki APs Reboot

API CODE: 200 = Successful
API CODE: 400 = Bad Request
API CODE: 403 = Forbidden
API CODE: 404 = Not Found
API CODE: 429 = Too Many Requests

{}

Executed from:
Server: {}
Directory: {}
""".format(sender, receiver, script_result, SRV_NAME, WORK_DIR)

# get server name and working directory
SRV_NAME = os.environ['COMPUTERNAME']
WORK_DIR = os.getcwd()

# Email execution
try:
    smtp_server.sendmail(sender, receiver, message)
    print('Email successfully sent')
except:
    print('Error: Unable to send email')

# closes the file.
f.close()