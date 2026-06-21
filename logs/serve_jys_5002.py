from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import os
ROOT = Path(r'D:\laborartory\大一下\项目\教师成果管理平台\jys-frontend')
BACKEND = 'http://127.0.0.1:5003'
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api'):
            self.proxy()
            return
        super().do_GET()
    def do_POST(self): self.proxy() if self.path.startswith('/api') else self.send_error(404)
    def do_PUT(self): self.proxy() if self.path.startswith('/api') else self.send_error(404)
    def do_PATCH(self): self.proxy() if self.path.startswith('/api') else self.send_error(404)
    def do_DELETE(self): self.proxy() if self.path.startswith('/api') else self.send_error(404)
    def translate_path(self, path):
        rel = path.split('?',1)[0].split('#',1)[0].lstrip('/')
        target = (ROOT / rel).resolve()
        try: target.relative_to(ROOT.resolve())
        except ValueError: return str(ROOT / 'index.html')
        if target.exists() and target.is_file(): return str(target)
        return str(ROOT / 'index.html')
    def proxy(self):
        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length) if length else None
        headers = {k:v for k,v in self.headers.items() if k.lower() not in {'host','content-length','connection','accept-encoding'}}
        req = Request(BACKEND + self.path, data=body, headers=headers, method=self.command)
        try:
            with urlopen(req, timeout=60) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in {'transfer-encoding','connection','content-encoding'}:
                        self.send_header(k, v)
                self.end_headers(); self.wfile.write(data)
        except HTTPError as e:
            data = e.read(); self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in {'transfer-encoding','connection','content-encoding'}:
                    self.send_header(k, v)
            self.end_headers(); self.wfile.write(data)
        except Exception as e:
            self.send_error(502, str(e))
    def log_message(self, format, *args): pass
os.chdir(ROOT)
ThreadingHTTPServer(('127.0.0.1', 5002), Handler).serve_forever()
