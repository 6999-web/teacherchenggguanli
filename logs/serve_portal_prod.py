from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os


ROOT = Path("/opt/teacherchenggguanli/current/portal")


os.chdir(ROOT)
ThreadingHTTPServer(("0.0.0.0", 5001), SimpleHTTPRequestHandler).serve_forever()
