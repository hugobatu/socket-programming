from rich import print
from bs4 import BeautifulSoup
import socket 

def getPageSrc():
	# URLs to try:
	# example.com
	# frogfind.com
	# info.cern.ch
	host = "pmichaud.com/toast"
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
	
	
def sendPageSrc(data):
	if data == "":
		data = """HTTP/1.1 200 OK
Date: Tue, 08 Aug 2023 08:32:43 GMT
Server: Apache
Expires: Tue, 01 Jan 2002 00:00:00 GMT
Cache-Control: no-cache
Set-Cookie: imstime=1691483563; expires=Thu, 07-Sep-2023 08:32:43 GMT; Max-Age=2592000; path=/
Last-Modified: Tue, 08 Aug 2023 08:32:43 GMT
Connection: close
Content-Type: text/html; charset=ISO-8859-1;

<!DOCTYPE html>
<html lang="en">
<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>A page</title>
</head>
<body>
		Hi there
</body>
</html>"""

	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("localhost", 80))
		
		s.listen(1)
		
		while True:
			c, addr = s.accept()
			
			print("About to send")
			c.send(data.encode())
			
			print("Sent")
			
			c.close()
			break
		
sendPageSrc("")