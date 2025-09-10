import string
import json


CONTEXT = {
    # "target": "http://localhost:1337",
    "target": "http://research.r3plican.dev:1337",
    "target_internal": "http://localhost:1337",
    "my_server": "http://lihxy-111-94-14-235.a.free.pinggy.link:42109",
    "hits": {},
    "survive": {}
}


emojis = ["^_^", ">_<", "owo", ":3", "uwu", "xD", "._.", "o_o", "T_T", "ಠ_ಠ", ":D", ":)", ":P", ";)", "-_-", ">:3", "♡", "｡^‿^｡", "(≧◡≦)", "ʕ•ᴥ•ʔ"]

log_folder = "./exfiltrate/"
latest_log = "data-10_42_36" 
with open(log_folder+ latest_log + ".json", "r") as f:
    CONTEXT = json.load(f)
