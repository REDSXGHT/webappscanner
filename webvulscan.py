import datetime

import requests,sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse,parse_qsl
from colorama import init,Fore

init()
r = Fore.RED
rt = Fore.RESET

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
session.headers["Cookie"] = "PHPSESSID=jsqpgdsjk4sridaflnadde82nf; security=low"

domain = sys.argv[1]

result = f'Web Vulnerability Scanner results for {domain} (Scanned at: {datetime.datetime.now()})\n\n'

with open(f"recon/{domain}/vuln_scan_result", 'w') as file:
    file.write(result)

def get_forms(url):
    soup = BeautifulSoup(session.get(url).content,'html.parser')
    return soup.find_all("form")

def form_details(form):
    detailsOfForm ={}

    try:
        action = form.attrs.get("action").lower()
        method = form.attrs.get("method").lower()

        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value","")
            inputs.append({"type":input_type,"name":input_name,"value":input_value})

        detailsOfForm['action'] = action
        detailsOfForm['method'] = method
        detailsOfForm['inputs'] = inputs

    except:
        detailsOfForm['action'] = '#'
        detailsOfForm['method'] = 'POST'
        detailsOfForm['inputs'] = [{"type": 'text', "name": 'name', "value": 'test'}]

    return detailsOfForm


def submit_form(details, url, data, payload=''):
    try:
        url = urljoin(url,details['action'])

        if details['method'] == 'post':
            res = session.post(url,data=data)
        else:
            res = session.get(url,params=data)
    except:
        res = session.get(url)

    return res


def sqli_vul(res):
    sqli_vuln_errors = ['you have an error in your sql syntax','quoted string not properly sanitized','unclosed quotation mark','warning: mysql']

    for errors in sqli_vuln_errors:
        if errors in res.content.decode().lower():
            return True
    return False


def sqli_scan_url(url, payload):

    url = urlparse(url)
    query_string = url.query
    pairs = query_string.split('&')
    for j in range(len(pairs)):
        pair = [pairs[j].split("=")[0],pairs[j].split("=")[1]+payload]
        pairs[j] = '='.join(pair)
    qs = '&'.join(pairs)
    mod_url= url.geturl().split('?')[0]+'?'+qs
    res = session.get(mod_url)
    return res


def xss_scan_url(url,payload):

    url = urlparse(url)
    query_string = url.query
    pairs = query_string.split('&')
    for j in range(len(pairs)):
        pair = [pairs[j].split('=')[0],pairs[j].split('=')[1]+payload]
        pairs[j] = '='.join(pair)
    qs = '&'.join(pairs)
    modified_url = url.geturl().split('?')[0]+'?'+qs
    res = session.get(modified_url)
    return res


def sqli_scan(url):
    global result

    forms = get_forms(url)
    print("[+]sqli Found {} forms in {}".format(len(forms), url))

    if len(forms)==0:
        return

    for form in forms:
        details = form_details(form)

        sqli_payload_list = ['\'','\"']

        for payload in sqli_payload_list:

            data = {}

            for input_tag in details['inputs']:
                if input_tag['type'] == 'hidden' or input_tag['value']:
                    data[input_tag['name']] = input_tag['value'] + payload
                elif input_tag['type'] != 'submit':
                    data[input_tag['name']] = f"test{payload}"

            res=submit_form(details,url,data,payload)

            if '?' in url:
                res=sqli_scan_url(url,payload)

            if sqli_vul(res):
                print(f"{r}[+]SQL Injection found on {url}.{rt}")
                result = f"SQL Injection found on {res.url} , Payload used : {payload} , Method: {details['method']}\n"
                with open(f"recon/{domain}/vuln_scan_result", 'a') as file:
                    file.write(result)
            else:
                pass


def xss_scan(url):
    global result
    forms = get_forms(url)
    print("[+]xss Found {} forms in {}".format(len(forms), url))

    if len(forms) == 0:
        return

    js_payload = "<Script>alert('XSS')</scripT>"

    for form in forms:
        details = form_details(form)

        data = {}

        for input_tag in details['inputs']:
            if input_tag['type'] == 'hidden' or input_tag['value']:
                data[input_tag['name']] = input_tag['value'] + js_payload
            elif input_tag['type'] != 'submit':
                data[input_tag['name']] = f"test{js_payload}"

        res=submit_form(details,url,data,js_payload)

        if '?' in url:
            res = xss_scan_url(url, js_payload)

        if js_payload in res.content.decode():
            print(f"{r}[+]Cross Site Scripting found on {url}.{rt}")
            result = f"Cross Site Scripting found on {res.url} , Payload used : {js_payload} , Method: {details['method']}\n"
            with open(f"recon/{domain}/vuln_scan_result",'a') as file:
                file.write(result)
        else:
            pass


if __name__ == "__main__":

    with open(f'recon/{domain}/crawl_output', 'r') as file:
        urls = file.read().splitlines()
        for url in urls:
            sqli_scan(url)
            xss_scan(url)
