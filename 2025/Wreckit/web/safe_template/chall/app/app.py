from flask import Flask, request, render_template, render_template_string, abort
import re
import unicodedata

app = Flask(__name__)

DANGEROUS_PATTERNS = [
    r"{%\s*",                           
    r"\|\s*safe\b",                     
    r"__\s*",                           
    r"\b(self|class|mro|subclasses|environment)\b",      
    r"\b(exec|eval|compile|breakpoint)\b", 
    r"\b(import|from|__import__|__globals__|__builtins__)\b",    
    r"\b(os|sys|subprocess|popen|system|pty|resource)\b",
    r"\b(request|config|url_for|get_flashed_messages|g)\b",
    r"\b(joiner|cycler|namespace)\b",
    r"\b(attr|getitem|setitem|delitem)\b",
    r"\bord\b",                        
    r"\+",                              
    r"\[\s*\d+\s*\]",                   
    r"`",                              
]

DANGEROUS_RE = re.compile("|".join(DANGEROUS_PATTERNS)) 

LEGACY_WORDS = [
    'exec', 'eval', 'request', 'config', 'dict', 'os', 'popen'
    'more', 'less', 'head', 'tail', 'nl', 'tac', 'awk', 'sed', 'grep',
    'ord',  
]

LEGACY_RE = re.compile("|".join(re.escape(w) for w in LEGACY_WORDS), re.I)
JINJA_EXPR_RE = re.compile(r"\{\{.*?\}\}")

def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    s = re.sub(r"\s+", "", s)
    return s

def check_payload(payload: str) -> bool:
    if not payload: return True
    if len(payload) > 400: return True

    flat = normalize(payload)
    print("flatten payload:", flat)

    found = DANGEROUS_RE.search(flat)
    if found: 
        print(found)
        return True
    
    found2 = LEGACY_RE.search(payload)
    if found2: 
        print(found)
        return True
    
    if "|" in payload: 
        print("'|' found")
        return True

    exprs = JINJA_EXPR_RE.findall(payload)
    if len(exprs) > 1:
        print("exprs > 1 not allowed")
        return True

    return False



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inputstring = request.form.get('inputstring', "")
        if check_payload(inputstring):
            return "Not allowed.", 400
        try:
            if JINJA_EXPR_RE.search(inputstring):
                template = f"{inputstring}\n"
                result = render_template_string(template)
            else:
                result = render_template_string("{{ value }}\n", value=inputstring)
        except Exception:
            print("Exception occured")
            return "Not allowed.", 400
        return result
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
