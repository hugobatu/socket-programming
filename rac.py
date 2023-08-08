from rich import print
from bs4 import BeautifulSoup
import socket 

# URLs to try:
# example.com
# frogfind.com
# info.cern.ch
host = "example.com"
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
s.connect((host, port))
sendMsg = "GET / HTTP/1.1\r\n"\
        "Host:" + host + "\r\n\r\n"
s.send(sendMsg.encode())

data = s.recv(4096)

# soup = BeautifulSoup(data.decode(), "html.parser")
# for a in soup.findAll('img'):
#     if (a['src'].find(host) == -1):
#         a['src'] = host + "/" + a['src'].lstrip("/")

print(data.decode())