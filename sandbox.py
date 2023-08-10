import socket 
import threading
from rich import print
from datetime import datetime
from bs4 import BeautifulSoup

page = """HTTP/1.1 200 OK
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Content-Type: text/html; charset=utf-8
Expires: -1
Server: Microsoft-IIS/10.0
X-AspNetMvc-Version: 5.2
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Date: Thu, 10 Aug 2023 16:02:17 GMT
Connection: close
Content-Length: 0


"""

pageUrl = "http://frogfind.com/"

# Định nghĩa host và port mà server sẽ chạy và lắng nghe
host = '192.168.56.1'
port = 4000

# TODO: append to turn relative JS script to absolute - update: damn i dont need to do that
def sendMessage(clientRequest):
	try:
		requestList = clientRequest.decode().split()
	except:
		print("Contains gzip")
		return
	
	hostStartIndex = clientRequest.decode().find("Host: ") + 6
	hostEndIndex = clientRequest.decode().find("\r\n", hostStartIndex)
	
	verb = requestList[0]
	resource = requestList[1]
	host = clientRequest.decode()[hostStartIndex: hostEndIndex]
	
	if resource[len(resource) - 1] == "/":
		resource = resource[:len(resource) - 1]
	
	print(f"verb: {verb}, resource: {resource}, host: {host}")
	
	return verb, resource, host
	

def proxy(url, msg):
	url = url.lstrip("/" ).rstrip("/")
	url = url.replace("http:/", "").lstrip("/")
	
	method, url, host = sendMessage(msg)
	
	print(f"Url: {url}")
	
	hostPage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		hostPage.connect((host, 80))
		sendMsg = f"{method} {url} HTTP/1.0\r\n"\
					"Host:" + host + "\r\n\r\n"
					
		print(f"Sending: {sendMsg}")
		hostPage.send(sendMsg.encode())

		response = b""
		while True:
			chunk = hostPage.recv(4096)
			if len(chunk) == 0:     # No more data received, quitting
				break
			response = response + chunk
		
		data = response
	except:
		data = page.encode()
	
	return data

def runTask(c, addr):
	while True:
		print("Start loop")
		try:
			msg = c.recv(1024)
		except:
			msg = ""
		if (not msg):
			print("No message")
			c.close()
			return
		
		try:
			print(f"Message received")
		except:
			print("UnicodeDecodeError: 'utf-8' codec can't decode byte ...")
		intro = str(datetime.now()) + "| Connect from " + str(addr)
		print(intro)
		
		sendMessage(msg)
		
		try:
			print(msg.decode())
		except:
			print("Cannot decode UNICODE")
			return
		
		msgList = msg.decode().split()
		
		if (msgList[0] == "GET"):
			print("Proxy")
			pageSrc = proxy(msgList[1], msg)
			
			sent = 0
			# print(f"Amount to send: {len(pageSrc.decode())}")
			# while sent < len(pageSrc.decode()):
			""" sent = sent +  """
			print("Bytes sent: ", c.send(pageSrc))
				# print(f"Sent: {sent}")
			
		

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))

	s.listen(3) # 1 ở đây có nghĩa chỉ chấp nhận 1 kết nối
	print("Server listening on port", port)



	print("before the while loop")
	while True:
		try:
			print("in the while loop")
			c, addr = s.accept()
			# thread = threading.Thread(target = runTask, args = (c, addr))
			# thread.start()
			runTask(c, addr)
			
		except KeyboardInterrupt:
			print("Closing program")
			c.close()

		
if __name__ == "__main__":
	main()
		