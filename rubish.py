import socket
import os
import datetime
from rich import print
from sandbox import *

msg = "GET http://oosc.online HTTP/1.0\r\nHost: oosc.online\r\n\r\n"
msg1 = "GET http://oosc.online/img/login/govt_logo.png HTTP/1.0\r\nHost: oosc.online\r\n\r\n"

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.connect(("oosc.online", 80))
    
    method, name, host = getRequestInfo(msg1.encode())
    server.send(msg1.encode())
    
    response = b""
    while True:
        chunk = server.recv(4096)
        if len(chunk) == 0:     # No more data received, quitting
            break
        response = response + chunk
    data = response
    
    print(data)
    
    
    # Caching
    name = name.replace("http://", "")
    if host != name:
        fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, name)
    else:
        fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, "index")
        
    fullPathName = fullPathName.replace("\\", "/")
    
    print(f"Folder: {host}, name: {name}, full path: {fullPathName}")
    # print(f"PATH: {os.path.dirname(os.path.abspath(__file__))}")
    
    createFile(fullPathName, data)
    
# main()

print(datetime.fromtimestamp(os.path.getmtime("C:/Users/phkhng/Documents/Code/socket-programming/đuôi.mèo")))