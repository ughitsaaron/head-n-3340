import os
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

url = "https://s3.amazonaws.com/personalprojects.aaronpetcoff/head-n-3340/main.txt"
PORT = os.environ.get("PORT") or 8000

if PORT == "None": PORT = 8000

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        with urllib.request.urlopen(url) as text:
            self.wfile.write(text.read())
        return


if __name__ == "__main__":
    with HTTPServer(("", int(PORT)), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()
