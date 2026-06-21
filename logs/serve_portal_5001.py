from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
ROOT = Path(r'D:\laborartory\大一下\项目\教师成果管理平台\portal')
os.chdir(ROOT)
ThreadingHTTPServer(('127.0.0.1', 5001), SimpleHTTPRequestHandler).serve_forever()
