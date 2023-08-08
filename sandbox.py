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
host = 'localhost'
port = 4000

# TODO: append to turn relative JS script to absolute
def proxy(url):
	url = url.lstrip("/").rstrip("/")
	
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
		msg = c.recv(1024)
		if (not msg):
			print("No message")
			c.close()
			return
		
		print("Message received")
		intro = str(datetime.now()) + "| Connect from " + str(addr)
		print(intro)
		#server sử dụng kết nối gửi dữ liệu tới client dưới dạng binary
		# c.send(b"Hello, how are you")
		# c.send(b"Bye\nHwllo world, programmed to work but not to feel")
		
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
			
		c.close()
		break
		# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# server.connect(("example.com", 80))
		# server.send(b"GET / HTTP/1.1\r\nHost:www.example.com\r\n\r\n")
		# data = server.recv(4096)
		# print(f"From page: {data.decode()}")
		
		
		# c.send(b"HTTP/1.0 200 OK\n")
		# c.send(b"Content-Type: text/html\n")
		# c.send(b"\n")
		# c.send(b"""
		#     <html>
		#     <body>
		#     <h1>Hello World</h1> this is my server!
		#     </body>
		#     </html>
		# """)
		
		# content = f"HTTP/1.1 200\r\nContent-Length: " + str(len(pageSrc)) + f"Content-Type: text/html\r\n" + pageSrc
		# c.send(content.encode())
		
		# while True:
		#   str = input("Enter your line: ")
		#   c.send(str.encode())
		
		# msg = c.recv(2048)
		# print(msg.decode())
		
		

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
		