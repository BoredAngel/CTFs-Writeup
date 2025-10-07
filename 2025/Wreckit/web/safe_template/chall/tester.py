import re
import unicodedata

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
    
    if "|" in payload: return True

    exprs = JINJA_EXPR_RE.findall(payload)
    if len(exprs) > 1:
        return True

    return False

print(check_payload("{{dir()}}"))

print([1,2,3][0x0])