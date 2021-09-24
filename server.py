#  coding: utf-8 
import socketserver
import email
from io import StringIO
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Changes made by Joshua Smith
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8") 
        print("Got a request of: %s\n" % self.data)
        requestLine, headers = self.data.split("\r\n", 1)
        message = email.message_from_file(StringIO(headers))
        headers = dict(message.items())
        method, path, typ = requestLine.split(' ', 2)
        if method != 'GET':
            r = "HTTP/1.1 405 OK\nContent-Type: text/plain\nContent-Length: 0\r\n"
        else:
            r = self.getFile(path)
        print(bytearray(r,'utf-8'))
        self.request.sendall(bytearray(r,'utf-8'))
        
    def getFile(self, requestPath):
        pathParts = requestPath.split("/")
        if len(pathParts) < 2:
            return self.ret404()
        i = 1
        path = os.getcwd()+ "/www/"
        while i < len(pathParts)-1:
            if pathParts[i] == "..":
                return self.ret404()
            #go to next directory
            if os.path.exists(path+pathParts[i]):
                path = path + pathParts[i] +"/"
                
                i+=1
            #if doesn't exist return 404
            else:
                return self.ret404()
        if pathParts[len(pathParts)-1] == '':
            path = path + "index.html"
            if os.path.isfile(path):
                return self.getFileResponseHTML(path)
            else:
                return self.ret404()
        path = path + pathParts[len(pathParts)-1]
        if os.path.isfile(path): 
            _ ,mimeType = pathParts[len(pathParts)-1].split(".")
            try:
                if mimeType == "html":
                    return self.getFileResponseHTML(path)
                elif mimeType == "css":
                    return self.getFileResponseCSS(path)
                else:
                    return self.getFileResponseOther(path)
            except:
                pass
        if os.path.exists(path):
            path = path + "/index.html"
            if os.path.isfile(path):
                return self.getFileResponseHTML301(path)
            else:
                return self.ret404()
        return self.ret404()
    
    def getFileResponseHTML(self, path):
        content = open(path, "r").read()
        x = "HTTP/1.1 200 OK\nContent-Type: text/html; charset=iso-8859-1\nConnection: close\nContent-Length: 1000\r\n" + content
        direct, _ = path.rsplit("/", 1)
        print("direct" + direct)
        for i in os.listdir(direct):
            try:
                _ ,mimeType = i.split(".")
                if mimeType == "css":
                    print(i)
                    x = x.replace(
                        '<link rel="stylesheet" type="text/css" href="' + i + '">',
                        "<style>" +(open((direct+"/"+i), "r").read()) + "</style>"
                    )
                    print(x)
            except:
                pass
        return x
    def getFileResponseHTML301(self, path):
        content = open(path, "r").read()
        return "HTTP/1.1 301 Moved Permanently\nContent-Type: text/html\nContent-Length: 1000\r\n" + content    
    def getFileResponseCSS(self, path):
        content = open(path, "r").read()
        return "HTTP/1.1 200 OK\nContent-Type: text/css\nContent-Length: 1000\r\n" + content
    def getFileResponseOther(self, path):
        content = open(path, "r").read()
        return "HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: 0\r\n" + content
    def ret404(self):
        return "HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: 0\r\n"
    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
