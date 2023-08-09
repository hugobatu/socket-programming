from rich import print
from bs4 import BeautifulSoup
import socket 

def getImage():
	HOST = 'frogfind.com'
	PORT = 80
	mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mysock.connect((HOST, PORT))
	print(f"Sending: GET http://frogfind.com/img/frogfind.gif HTTP/1.0\r\n\r\n")
	mysock.sendall(b'GET http://frogfind.com/img/frogfind.gif HTTP/1.0\r\n\r\n')
	count = 0
	picture = b""

	while True:
		data = mysock.recv(5120)
		if len(data) < 1: break
		#time.sleep(0.25)
		count = count + len(data)
		print(len(data), count)
		picture = picture + data

	mysock.close()

	# Look for the end of the header (2 CRLF)
	pos = picture.find(b"\r\n\r\n")
	print('Header length', pos)
	print(picture[:pos].decode())

	print(picture)

	# Skip past the header and save the picture data
	picture = picture[pos+4:]
	fhand = open("stuff.jpg", "wb")
	fhand.write(picture)
	fhand.close()

def getPageSrc(url = ""):
	# URLs to try:
	# example.com
	# frogfind.com
	# info.cern.ch
	
	if url != "":
		host = url.split("/")[0]
	else:
		host = "pmichaud.com"
		url = host
		
	port = 80

	print(f"URL: {host}")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
	s.connect((host, port))
	sendMsg = "GET http://" + url + " HTTP/1.0\r\n\r\n"
	
	print(f"Sending: {sendMsg}")
	# return
	s.sendall(sendMsg.encode())

	data = s.recv(4096)

	# soup = BeautifulSoup(data.decode(), "html.parser")
	# for a in soup.findAll('img'):
	#     if (a['src'].find(host) == -1):
	#         a['src'] = host + "/" + a['src'].lstrip("/")


	print(data)
	
	
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
		
# sendPageSrc("")
# getPageSrc("frogfind.com/img/frogfind.gif")
getImage()