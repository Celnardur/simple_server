#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import json
import os
import mimetypes
import sys
# import api

bufsize = 4096
base_path = "./www"

class server(BaseHTTPRequestHandler):
    def get_payload(self):
        if not ('Content-Length' in self.headers):
            return (200, None)

        try:
            content_length = int(self.headers['Content-Length'])
        except ValueError:
            return (400, b"Malformed content_length")

        if content_length <= 0:
            return (200, None)

        try:
            return (200, json.loads(self.rfile.read(int(content_length))))
        except:
            return (400, b"Malformed json payload")

    def file_response(self, path):
        response_code = 200

        if not os.path.exists(path):
            response_code = 404
            path = os.path.join(base_path, '404.html')
            if not os.path.exists(path):
                self.code_response(404, b'404')
                return


        if not os.path.isfile(path):
            path = os.path.join(path, 'index.html')

        mime_type, _ = mimetypes.guess_type(path)
        self.send_response(response_code)
        self.send_header('Content-Type', mime_type)
        self.end_headers()
        with open(path, 'rb') as out_file:
            buf = out_file.read(bufsize)
            while len(buf) > 0:
                self.wfile.write(buf)
                buf = out_file.read(bufsize)

    def code_response(self, response_code, content):
        self.send_response(response_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(content)


    def do_GET(self):
        url = self.path.split("?")
        path = os.path.join(base_path, url[0][1:])
        self.file_response(path)

    def do_PUT(self):
        (code, payload) = self.get_payload()
        # handle malformed payload
        if code == 400:
            self.code_response(400, bytes(payload, 'utf-8'))
            return

        print(payload)
        url = self.path.split("?")
        path = os.path.join(base_path, url[0][1:])
        self.file_response(path)
        # if url[0][:4] == '/api':
        #     try:
        #         (code, body) = api.process(url[0][4:], payload)
        #         if code == 200:
        #             api.get_notifications(url[0][4:], payload)
        #     except:
        #         self.code_response(500, b'Internal Server Error')
        #         return
                
        #     self.send_response(code)
        #     self.send_header('Content-Type', 'application/json')
        #     self.end_headers()
        #     self.wfile.write(bytes(json.dumps(body), 'utf-8'))
        # else:
        #     path = os.path.join(base_path, url[0][1:])
        #     self.file_response(path)




def usage():
    print("Usage: ./server.py [options]")
    print("    -h, --help        print this help and exit")
    print("    -n, --host_name   set the server host name")
    print("    -p, --port        set the server port number")
    print("    -b, --base_path   set the base path to serve files from")

if __name__ == "__main__":
    host_name = "localhost"
    server_port = 8080

    arg_n = 1
    arg_len = len(sys.argv)
    while arg_n < arg_len:
        arg = sys.argv[arg_n]
        if arg.startswith("-"):
            if arg == "--host_name" or arg == "-n":
                host_name = sys.argv[arg_n + 1]
            elif arg == "--port" or arg == "-p":
                server_port = int(sys.argv[arg_n + 1])
            elif arg == "--base_path" or arg == "-b":
                base_path = sys.argv[arg_n + 1]
                if not os.path.isdir(base_path):
                    print("Specified base path does not exist")
                    exit(1)
            elif arg == "--help" or arg == "-h":
                usage()
                exit(0)
            else:
                usage()
                exit(1)
            arg_n += 1
        arg_n += 1

    if not os.path.exists(base_path) or not os.path.isdir(base_path):
        print("Specified base path " + base_path + " does not exist")
        exit(1)

    print("Host name: " + host_name)
    print("server port: " + str(server_port))
    print("base path: " + base_path)

    # api.init()
    httpd = HTTPServer((host_name, server_port), server)
    httpd.serve_forever()

