import requests,json,sys
import urllib3

urllib3.disable_warnings()

domain = sys.argv[1]

with open(f"recon/{domain}/vuln_scan_result","r")as file:
    result = file.read()

credentials = 'creds.json'
message = result

def get_credentials(credentials):
    with open(credentials,'r')as file:
        creds = json.loads(file.read())
    return creds['slack_webhook']

def post_to_slack(message,credentials):
    data = {'text':message}
    url = get_credentials(credentials)
    res = requests.post(url,json=data,verify=False)

post_to_slack(message,credentials)


