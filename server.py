"""StudentAI backend. No installs needed (Python standard library only).
Serves the website and answers /api/chat using the AI key stored in config.txt (never sent to the browser)."""
import json, os, sys, threading, time, urllib.error, urllib.request, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
BLOCK = ("config.txt", "server.py", "start.bat", ".gitignore", ".env")
HITS = {}

def cfg():
    c = {}
    p = os.path.join(ROOT, "config.txt")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8-sig"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                c[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("GEMINI_API_KEY", "GEMINI_MODEL", "GROQ_API_KEY", "GROQ_MODEL", "PORT"):
        if os.environ.get(k):
            c[k] = os.environ[k]
    return c

def real(v):
    return bool(v) and not v.lower().startswith("paste")

def post(url, headers, body, timeout=60):
    req = urllib.request.Request(url, json.dumps(body).encode(), dict({"Content-Type": "application/json"}, **headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": {"message": "unreachable: " + str(e)}}

def gemini(c, msgs, image):
    model = c.get("GEMINI_MODEL") or "gemini-3.8-flash"
    contents = [{"role": "model" if m.get("role") == "assistant" else "user", "parts": [{"text": str(m.get("content", ""))[:6000]}]} for m in msgs[-8:]]
    if not contents:
        return 400, "No message"
    if image:
        contents[-1]["parts"].append({"inlineData": {"mimeType": "image/jpeg", "data": image}})
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model
    h = {"x-goog-api-key": c["GEMINI_API_KEY"]}
    s, j = post(url, h, {"contents": contents, "generationConfig": {"thinkingConfig": {"thinkingLevel": "low"}}})
    if s != 200:
        s, j = post(url, h, {"contents": contents})
    if s == 200:
        parts = (((j.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or []
        return 200, "".join(p.get("text", "") for p in parts)
    return s, (j.get("error") or {}).get("message", "AI error")

def groq(c, msgs):
    model = c.get("GROQ_MODEL") or "openai/gpt-oss-120b"
    m = [{"role": x.get("role", "user"), "content": str(x.get("content", ""))[:6000]} for x in msgs[-8:]]
    s, j = post("https://api.groq.com/openai/v1/chat/completions", {"Authorization": "Bearer " + c["GROQ_API_KEY"]}, {"model": model, "messages": m})
    if s == 200:
        return 200, j["choices"][0]["message"]["content"]
    return s, (j.get("error") or {}).get("message", "AI error")

def chat(body, ip):
    c = cfg()
    now = time.time()
    h = [t for t in HITS.get(ip, []) if now - t < 60]
    if len(h) >= 30:
        return 429, {"error": "Too many requests, please wait a minute"}
    h.append(now); HITS[ip] = h
    msgs = body.get("msgs") or []
    err = "No AI key is set. Open config.txt and paste your key."
    if real(c.get("GEMINI_API_KEY", "")):
        s, t = gemini(c, msgs, body.get("image"))
        if s == 200 and t:
            return 200, {"text": t, "via": "gemini"}
        err = t if isinstance(t, str) else "AI error"
    if real(c.get("GROQ_API_KEY", "")) and not body.get("image"):
        s, t = groq(c, msgs)
        if s == 200 and t:
            return 200, {"text": t, "via": "groq"}
        err = t if isinstance(t, str) else err
    return 502, {"error": "AI unreachable or limit reached: " + err}

class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def send_json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def blocked(self):
        return os.path.basename(self.path.split("?")[0]).lower() in BLOCK
    def do_GET(self):
        if self.path.startswith("/api/chat"):
            c = cfg()
            return self.send_json(200, {"ok": real(c.get("GEMINI_API_KEY", "")) or real(c.get("GROQ_API_KEY", ""))})
        if self.blocked():
            return self.send_json(404, {"error": "Not found"})
        return super().do_GET()
    def do_POST(self):
        if not self.path.startswith("/api/chat"):
            return self.send_json(404, {"error": "Not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(min(n, 8_000_000)) or b"{}")
        except Exception:
            return self.send_json(400, {"error": "Bad request"})
        code, out = chat(body, self.client_address[0])
        self.send_json(code, out)

def main():
    c = cfg()
    hosted = bool(os.environ.get("PORT"))
    port = int(c.get("PORT") or 8000)
    host = "0.0.0.0" if hosted else "127.0.0.1"
    srv = None
    for p in range(port, port + 10):
        try:
            srv = ThreadingHTTPServer((host, p), H); port = p; break
        except OSError:
            continue
    if not srv:
        print("Could not open a port. Close other programs and try again."); return
    url = "http://localhost:%d" % port
    print("\n  StudentAI is running at " + url)
    if not (real(c.get("GEMINI_API_KEY", "")) or real(c.get("GROQ_API_KEY", ""))):
        print("  NOTE: no AI key found. Open config.txt in Notepad and paste your key, then restart.")
    print("  Keep this window open. Close it to stop.\n")
    if not hosted:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
