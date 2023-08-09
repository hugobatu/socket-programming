import socket 
import threading
from rich import print
from datetime import datetime
from bs4 import BeautifulSoup

page = """<!DOCTYPE html>
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

pageUrl = "http://frogfind.com/"

# Định nghĩa host và port mà server sẽ chạy và lắng nghe
host = '192.168.56.1'
port = 4000

# TODO: append to turn relative JS script to absolute - update: damn i dont need to do that
def proxy(url):
	url = url.lstrip("/"
		  ).rstrip("/")
	url = url.replace("http:/", "").lstrip("/")
	
	print(f"Url: {url}")
	
	hostPage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		hostPage.connect((url, 80))
		sendMsg = "GET / HTTP/1.0\r\n"\
					"Host:" + url + "\r\n\r\n"
		hostPage.send(sendMsg.encode())

		data = hostPage.recv(4096)
	except:
		data = page.encode()
	
	soup = BeautifulSoup(data.decode(), "html.parser")
	for a in soup.findAll('img'):
		if (a['src'].find(url) == -1):
			a['src'] = "#"
	
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
		
		print(f"Message received: {msg}")
		intro = str(datetime.now()) + "| Connect from " + str(addr)
		print(intro)
		
		print(msg.decode())
		
		msgList = msg.decode().split()
		
		if (msgList[0] == "GET"):
			print("Proxy")
			pageSrc = proxy(msgList[1])
			print(pageSrc.decode())
			
			sent = 0
			print(f"Amount to send: {len(pageSrc.decode())}")
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
		