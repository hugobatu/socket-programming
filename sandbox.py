import socket 
import threading
import configparser
import json
import os
from rich.console import Console
console = Console()
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

global cache_time, whitelisting, time
pageUrl = "http://frogfind.com/"

# Định nghĩa host và port mà server sẽ chạy và lắng nghe
host = 'localhost'
port = 4000


# abridged function added
def abridgedPrint(data, limit):
	if len(data) <= limit:
		print(data)
	else:
		print(data[:limit-1] + ".")


# TODO: append to turn relative JS script to absolute - update: damn i dont need to do that
def getConfig():
	fileConfig = open('config.mèo')
	configs = json.load(fileConfig)
	return configs['cache_time'], configs['whitelisting'], configs['time']		

def createFile(fileName, content):
	try:
		console.print(f"Creating {os.path.dirname(fileName)}", style="purple4")
		
		# Neu folder khong ton tai -> tao folder
		os.makedirs(os.path.dirname(fileName), exist_ok=True)
		
		# Ghi file
		with open(fileName, "wb") as f:
			f.write(content)
	except:
		console.print("Wrong file path", style="red bold")
	

def getRequestInfo(clientRequest):
	# Tach request cua Client tai moi dau cach, tao thanh mot mang chua cac thong tin
	try:
		requestList = clientRequest.decode().split()
	# Neu khong the tach duoc -> Ket thuc ham
	except:
		console.print("Contains gzip")
		return	
	
	# Tim vi tri bat dau va ket thuc cua host, ie. Host: info.cern.ch
	hostStartIndex = clientRequest.decode().find("Host: ") + 6
	hostEndIndex = clientRequest.decode().find("\r\n", hostStartIndex)
	
	# Cac bien de tra ve
	method = requestList[0]
	resource = requestList[1]
	host = clientRequest.decode()[hostStartIndex: hostEndIndex]
	
	if resource[len(resource) - 1] == "/":
		resource = resource[:len(resource) - 1]
	
	# console.print(f"verb: {verb}, resource: {resource}, host: {host}")
	
	return method, resource, host
	
def checkCache(msg):
	method, url, host = getRequestInfo(msg)
	
	# Tao ten file de luu cache
	# Xoa http://
	name = url.replace("http://", "")
	
	# Neu ten Resource khac ten Host -> them Resource o cuoi duong dan
	if host != name:
		fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, name)
	# Neu giong nhau -> them index o cuoi duong dan
	else:
		fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, "index")
		# fullPathName = c:/Users/phkhng/Documents/Code/socket-programming/cache/oosc.online/index
		
	fullPathName = fullPathName.replace("\\", "/")
	
	data = b""
	isExist = True
	if not os.path.isfile(fullPathName):
		console.print(f"No cache", style="deep_pink3")
		isExist = False
	else:
		console.print(f"Taking from cache: {fullPathName}", style="deep_pink3")
		with open(fullPathName, "rb") as fp:
			data = fp.read()	
	
	return data, fullPathName, isExist

def proxy(url, msg):
	method, url, host = getRequestInfo(msg)
	
	console.print(f"Url: {url}")
	
	cache, fullPathName, isExist = checkCache(msg)
	
	if (isExist):
		cache = cache.partition(b"\r\n\r\n")[0]
		try:
			console.print(f"--> :{cache.decode()}", style="bold cyan")
		# Neu co ky tu UNICODE trong data -> In tat ca duoi dang nhi phan
		except:
			print(f"--> :{cache}")
		return cache
	else:
		print()

	# Neu file cache cua request co ton tai -> Request nguon tu web server va luu cache
	console.print(f"Get fresh source", style="deep_pink3")
	hostPage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Thu ket noi web server: Ket noi thanh cong -> Gui sendMsg toi server va nhan ket qua vao data
	try:
		# Ket noi toi web server
		hostPage.connect((host, 80))
		
		# Tao request gui toi web server
		if (method == "GET" or method == "HEAD"):
			sendMsg = f"{method} {url} HTTP/1.1\r\n"\
						"Host: " + host + "\r\n"\
						"Connection: close\r\n\r\n"
		elif (method == "POST"):
			sendMsg = f"{method} {url} HTTP/1.1\r\n"
			sendMsg += msg.decode().partition("\r\n")[2]
			sendMsg = sendMsg[:sendMsg.find("Connection:")] + "Connection: close" + sendMsg[sendMsg.find("\r\n", sendMsg.find("Connection:")):]
		else:
			return
		
		console.print(f"Sending: {sendMsg}")
		hostPage.send(sendMsg.encode())

		# Nhan ve ket qua server vao tung mau kich thuoc 4096 -> Gop lai thanh mot bai hoan chinh
		response = b""
		while True:
			chunk = hostPage.recv(4096)
			if len(chunk) == 0:     # No more data received, quitting
				break
			response = response + chunk
		
		data = response
		
		createFile(fullPathName, data)
	
	# Ket noi khong thanh cong -> data = page (da tao tu truoc)
	except Exception as e:
		print(e)
		data = page.encode("ISO-8859-1")
	
	if (method == "HEAD"):
		data = data.partition(b"\r\n\r\n")[0]
	
	# In ra ket qua nhan ve tu web server
	# Neu khong co ky tu UNICODE trong data -> Moi dung duoc .decode (chuyen tu thong tin nhi phan sang string)
	try:
		console.print(f"--> :{data.decode()}", style="bold cyan")
	# Neu co ky tu UNICODE trong data -> In tat ca duoi dang nhi phan
	except:
		print(f"--> :{data}")
		
	return data

def runTask(client, addr):
	while True:
		console.print("------------------------------------------")
		console.print("New user", style="bold green")
		
		# Nhan ve request cua Client (trinh duyet)
		try:
			msg = client.recv(1024)
		except:
			msg = ""
			
		if (not msg):
			console.print("No message\n", style="bold red")
			client.close()
			return
		
		try:
			console.print(f"Message received")
		except:
			console.print("UnicodeDecodeError: 'utf-8' codec can't decode byte ...")
		
		# In ra thong tin Client: thoi gian, dia chi IP
		intro = str(datetime.now()) + " | Connect from " + str(addr)
		console.print(intro, style="bold")
		
		# Phan tich cac thanh phan request cua Client va tra ra: 
		# Method (GET, HEAD, POST,...),
		# Resource (ie. frogfind.com, oosc.online/style.css,...),
		# Host: ten trang web
		getRequestInfo(msg)
		
		# In request cua Client
		try:
			console.print(msg.decode())
		except:
			console.print("Cannot decode UNICODE", style="bold red")
			return
		
		# if (time.partition("-")[0] <= ):
		
		msgList = msg.decode().split()
		
		# Cac thanh phan request cua Client: 
		# msgList[0]: Method (GET, HEAD, POST,...),
		# msgList[0]: Resource (ie. frogfind.com, oosc.online/style.css,...),
		# msgList[0]: Host: ten mien trang web
		if (msgList[0] == "GET"):
			console.print("Get")
			pageSrc = proxy(msgList[1], msg)
			
			# Gui ket qua cua web server ve lai Client
			console.print("Bytes sent: ", client.send(pageSrc))
			
		elif (msgList[0] == "POST"):
			console.print("Post")
			pageSrc = proxy(msgList[1], msg)
			
			# Gui ket qua cua web server ve lai Client
			console.print("Bytes sent: ", client.send(pageSrc))
		
		
		client.close()
			
def main():
	cache_time, whitelisting, time = getConfig()
	
	print(f"cache_time: {cache_time}, whitelisting: {whitelisting}, time: {time}")
	
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host, port))

	server.listen(3) # 3 ở đây có nghĩa chỉ chấp nhận 3 kết nối
	console.print("Server listening on port", port)


	while True:
		try:
			console.print("Waiting for new user", style="bold yellow")
			client, addr = server.accept()
			# thread = threading.Thread(target = runTask, args = (client, addr))
			# thread.start()
			runTask(client, addr)
			
		except KeyboardInterrupt:
			console.print("Closing program")
			client.close()

		
if __name__ == "__main__":
	main()