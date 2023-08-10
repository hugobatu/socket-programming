from rich import print
from bs4 import BeautifulSoup
import socket 
import zlib

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
	
	# Neu url trong thi dung url default
	if url != "":
		host = url.split("/")[0]
	else:
		host = "pmichaud.com"
		url = host
		
	port = 80

	# In thu url (de test)
	print(f"URL: {host}")
	
	# Ket noi voi trang web
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
	s.connect((host, port))
	
	# Tao msg de khoi tao ket noi
	sendMsg = "GET http://" + url + " HTTP/1.0\r\n\r\n"
	print(f"Sending: {sendMsg}")
	
	# Khoi tao ket noi
	s.sendall(sendMsg.encode())

	# Nhan lai HTML cua trang
	data = s.recv(4096)

	# In HTML cua trang
	print(data.decode())
	
	
def sendPageSrc(data):
	# data = data.encode()
	if data == "":
		data = testClientRequest()

	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("localhost", 80))
		
		s.listen(1)
		
		while True:
			c, addr = s.accept()
			
			print("About to send")
			c.send(data)
			
			print("Sent")
			
			c.close()
			break
		
def testClientRequest():
	host = "oosc.online"
	port = 80
	
	# Ket noi voi trang web
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
	s.connect((host, port))
	
	# Tao msg de khoi tao ket noi
	sendMsg = f"GET / HTTP/1.0\r\nHost: {host}\r\n\r\n"
	sendMsg = """GET http://oosc.online/Content/loginstyles.css HTTP/1.1
Host: oosc.online
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0
Accept: text/css,*/*;q=0.1
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://oosc.online/
Cookie: imstime=1691483563
Pragma: no-cache
Cache-Control: no-cache

"""
	print(f"Sending: {sendMsg}")
	
	
	# Khoi tao ket noi
	s.sendall(sendMsg.encode())

	# Nhan lai HTML cua trang
	data = s.recv(4096)

	# In HTML cua trang
	print("Receiving:")
	print(data)
	
	return data
		
# sendPageSrc("")
getPageSrc()
# testClientRequest()
# getImage()


# GET http://oosc.online/Content/loginstyles.css HTTP/1.1
# Host: oosc.online
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0
# Accept: text/css,*/*;q=0.1
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate
# Connection: keep-alive
# Referer: http://oosc.online/
# Cookie: imstime=1691483563
# Pragma: no-cache
# Cache-Control: no-cache