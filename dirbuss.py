import requests,threading,queue,sys,time

host = sys.argv[1]
threads = int(sys.argv[2])
ext = sys.argv[3]

result=f'Directory buster results for : {host} \n \n'

with open(f"recon/{host.split('/')[2]}/dirbuss_res",'w') as file:
    file.write(result)

try:
    requests.get(host)
except Exception as e:
    print(e)
    exit(0)

directory_list = open('wordlist/common.txt','r')           #Go to wordlist directory and add new wordlists , then make changes here.

q= queue.Queue()
count = 0
res = ' '
start_time=time.time()

def dirbuss(thread_no,q):
    global count,res
    while not q.empty():
        url = q.get()
        try:
            response = requests.get(url,allow_redirects=True,timeout=2)
            count += 1
            print(f"[+]Tried Directories {count}",end='\r')
            if response.status_code == 200:
                res +=f"{str(response.url)} \n"
        except:
            pass

        q.task_done()

for directory in directory_list.read().splitlines():
    if not ext:
        url = host + '/' + directory
    else:
        url = host + '/' + directory + ext

        q.put(url)


for i in range(threads):
    t=threading.Thread(target=dirbuss,args=(i,q))
    t.daemon=True
    t.start()


q.join()
end_time = time.time()
print("\n[+]Directories Found: \n")
print(res)
with open(f"recon/{host.split('/')[2]}/dirbuss_res", 'a') as file:
    file.write(res)
print("[+]Time taken: {}".format(end_time-start_time))

