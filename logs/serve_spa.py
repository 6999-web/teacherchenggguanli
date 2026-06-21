from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import os, sys

ROOT = Path(sys.argv[1]).resolve()
PORT = int(sys.argv[2])
BACKEND = sys.argv[3] if len(sys.argv) > 3 else ''
os.chdir(ROOT)

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        rel = path.split('?', 1)[0].split('#', 1)[0].lstrip('/')
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            return str(ROOT / 'index.html')
        if target.exists() and target.is_file():
            return str(target)
        return str(ROOT / 'index.html')

    def do_GET(self):
        if BACKEND and (self.path.startswith('/api') or self.path.startswith('/uploads')):
            return self.proxy()
        return super().do_GET()

    def do_POST(self):
        return self.proxy() if BACKEND and self.path.startswith('/api') else self.send_error(404)
    def do_PUT(self):
        return self.proxy() if BACKEND and self.path.startswith('/api') else self.send_error(404)
    def do_PATCH(self):
        return self.proxy() if BACKEND and self.path.startswith('/api') else self.send_error(404)
    def do_DELETE(self):
        return self.proxy() if BACKEND and self.path.startswith('/api') else self.send_error(404)

    def proxy(self):
        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length) if length else None
        headers = {k:v for k,v in self.headers.items() if k.lower() not in {'host','content-length','connection','accept-encoding'}}
        try:
            req = Request(BACKEND + self.path, data=body, headers=headers, method=self.command)
            with urlopen(req, timeout=60) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in {'transfer-encoding','connection','content-encoding'}:
                        self.send_header(k, v)
                self.end_headers(); self.wfile.write(data)
        except HTTPError as e:
            data=e.read(); self.send_response(e.code); self.end_headers(); self.wfile.write(data)
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, fmt, *args):
        pass

ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
