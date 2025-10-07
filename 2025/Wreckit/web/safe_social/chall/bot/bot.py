import os
import time
import requests
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

API_BASE = os.environ.get("API_BASE", "http://backend:10003")
FRONTEND_BASE = os.environ.get("FRONTEND_BASE", "http://frontend:5173")
USERNAME = "admin"
PASSWORD = "REDACTED"
COOKIE_NAME = "session"

LOGIN_INTERVAL = int(os.environ.get("LOGIN_INTERVAL", "120"))
VISIT_DELAY_SECONDS = int(os.environ.get("VISIT_DELAY_SECONDS", "10"))
NAV_TIMEOUT_MS = int(os.environ.get("NAV_TIMEOUT_MS", "10000"))
POST_NAV_PAUSE_MS = int(os.environ.get("POST_NAV_PAUSE_MS", "500"))
REFRESH_INTERVAL_SEC = int(os.environ.get("REFRESH_INTERVAL_SEC", "10"))

VISIT_COOLDOWN_SEC = int(os.environ.get("VISIT_COOLDOWN_SEC", "10"))

def api_login_and_get_posts():
    try:

        s = requests.Session()
        r = s.post(f"{API_BASE.rstrip('/')}/api/login",
                   json={"username": USERNAME, "password": PASSWORD}, timeout=5)
        if r.status_code != 200 or not r.json().get("ok"):
            return None, None
        print("Bot Logging in as admin")
        return s, fetch_posts(s)
    except Exception:
        return None, None

def fetch_posts(session):
    try:
        r2 = session.get(f"{API_BASE.rstrip('/')}/api/posts", timeout=5)
        print(f"bot fetching for post")
        return r2.json() if r2.status_code == 200 else []
    except Exception:
        return []

def extract_cookie_value(rsession, cookie_name=COOKIE_NAME):
    for c in rsession.cookies:
        if c.name == cookie_name:
            return c.value
    return None

def host_from_base(url):
    try:
        return urlparse(url).hostname or "frontend"
    except Exception:
        return "frontend"

def run():
    frontend_host = host_from_base(FRONTEND_BASE)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = context.new_page()

        try:
            last_login_time = 0.0
            session = None
            posts = []
            cookie_val = None
            last_refresh = 0.0

            visited_at = {} 

            while True:
                now = time.monotonic()

                if session is None or (now - last_login_time) >= LOGIN_INTERVAL:
                    session, posts = api_login_and_get_posts()
                    if session is not None:
                        cookie_val = extract_cookie_value(session, COOKIE_NAME) or ""
                        last_login_time = time.monotonic()
                        last_refresh = 0.0
                        try:
                            context.clear_cookies()
                        except Exception:
                            pass
                        if cookie_val:
                            try:
                                context.add_cookies([{
                                    "name": COOKIE_NAME,
                                    "value": cookie_val,
                                    "domain": frontend_host,
                                    "path": "/",
                                    "httpOnly": True,
                                    "secure": False,
                                    "sameSite": "Lax",
                                }])
                            except Exception:
                                pass
                    else:
                        posts = []
                        cookie_val = None
                        time.sleep(5)
                        continue

                if (time.monotonic() - last_refresh) >= REFRESH_INTERVAL_SEC:
                    refreshed = fetch_posts(session)
                    if isinstance(refreshed, list) and refreshed:
                        posts = refreshed
                    last_refresh = time.monotonic()

                if not posts:
                    time.sleep(REFRESH_INTERVAL_SEC)
                    continue

                print("Posts:", posts)

                for p in posts:
                    if (time.monotonic() - last_refresh) >= REFRESH_INTERVAL_SEC:
                        refreshed = fetch_posts(session)
                        if isinstance(refreshed, list) and refreshed:
                            posts = refreshed
                        last_refresh = time.monotonic()

                    if (time.monotonic() - last_login_time) >= LOGIN_INTERVAL:
                        break

                    hid = p.get("id")
                    if not hid:
                        continue

                    last = visited_at.get(hid, 0.0)
                    if VISIT_COOLDOWN_SEC > 0 and (time.monotonic() - last) < VISIT_COOLDOWN_SEC:
                        continue

                    frontend_url = f"{FRONTEND_BASE.rstrip('/')}/post/{hid}"

                    try:
                        page.goto(frontend_url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
                    except Exception:
                        try:
                            page.goto(frontend_url, wait_until="domcontentloaded", timeout=2 * NAV_TIMEOUT_MS)
                        except Exception:
                            continue

                    try:
                        page.wait_for_timeout(POST_NAV_PAUSE_MS)
                    except Exception:
                        pass

                    time.sleep(VISIT_DELAY_SECONDS)
                    visited_at[hid] = time.monotonic()

                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            try: page.close()
            except Exception: pass
            try: context.close()
            except Exception: pass
            try: browser.close()
            except Exception: pass

if __name__ == "__main__":
    run()
