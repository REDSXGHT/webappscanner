import os.path

import requests,sys,threading,queue

host = sys.argv[1]
threads = int(sys.argv[2])

recon_dir_path= 'recon/' + host

if not os.path.exists(recon_dir_path):
    os.mkdir(recon_dir_path)

with open(recon_dir_path + '/subdomains','w') as file:
    file.write(host + '\n')

q = queue.Queue()

print("[+] Starting to find subdomains ... ")

def subbrute():
    while not q.empty():
        subdomain = q.get()
        url = f"http://{subdomain}.{host}"
        try:
            response = requests.get(url,allow_redirects=False,timeout=2)
            if response.status_code == 200:
                subd = response.url.split('/')[2]
                print(f"[+]Subdomain found {subd}")
                with open(recon_dir_path + '/subdomains','a') as file:
                    file.write(subd+'\n')
        except:
            pass

        q.task_done()


with open('wordlist/common.txt','r') as file:        #Go to wordlist directory and add new wordlists , then make changes here.
    subdomains = file.read().splitlines()
    for subdomain in subdomains:
        q.put(subdomain)

for i in range(threads):
    t = threading.Thread(target=subbrute,daemon=True)
    t.start()

q.join()

