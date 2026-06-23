import http.server
import socketserver
import os

os.chdir('E:\\xweb\\akayok\\AKAYOK')

PORT = 5000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
