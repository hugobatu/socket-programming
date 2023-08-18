import socket
import os
import gzip
import datetime
from rich import print
from sandbox import *

msg = "POST /userinfo.php HTTP/1.1\r\nHost: testphp.vulnweb.com\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\nContent-Length: 20\r\n\r\nuname=hihg&pass=high"
msg1 = "GET http://oosc.online/img/login/govt_logo.png HTTP/1.0\r\nHost: oosc.online\r\n\r\n"
msg2 = "GET http://testphp.vulnweb.com/login.php HTTP/1.1"\
"\r\nHost: testphp.vulnweb.com"\
"\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"\
"\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"\
"\r\nAccept-Language: en-US,en;q=0.5"\
"\r\nAccept-Encoding: gzip, deflate"\
"\r\nReferer: http://testphp.vulnweb.com/login.php"\
"\r\nConnection: close"\
"\r\nUpgrade-Insecure-Requests: 1\r\n\r\n"

def main():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind(("localhost", 4000))
    proxy.listen(1)
    client, addr = proxy.accept()
    print("Connected")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    method, name, host = getRequestInfo(msg2.encode())
    
    server.connect((host, 80))
    
    server.send(msg2.encode())
    
    response = b""
    while True:
        chunk = server.recv(4096)
        if len(chunk) == 0:     # No more data received, quitting
            break
        response = response + chunk
    data = response
    
    # print(gzip.decompress(data[data.decode("iso-8859-2").find("\r\n\r\n") + 4:]))
    # data.decode("iso-8859-2")
    
    
    # Caching
    name = name.replace("http://", "")
    if host != name:
        fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, name)
    else:
        fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, "index")
        
    fullPathName = fullPathName.replace("\\", "/")
    
    print(f"Folder: {host}, name: {name}, full path: {fullPathName}")
    # print(f"PATH: {os.path.dirname(os.path.abspath(__file__))}")
    
    # createFile(fullPathName, data)
    
    client.send(data)
    print("Sent")
    
# main()

print(datetime.fromtimestamp(os.path.getmtime("C:/Users/phkhng/Documents/Code/socket-programming/đuôi.mèo")).hour)