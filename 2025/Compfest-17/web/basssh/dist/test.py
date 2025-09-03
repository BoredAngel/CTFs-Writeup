
import requests


r = requests.post("http://localhost:3000/?file=add2num.py", data={"input":"--help"})
print(r.text)