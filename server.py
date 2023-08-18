import socket 
import threading
import configparser
import json
import os
from rich.console import Console
console = Console()
import datetime

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

# Định nghĩa host và port mà server sẽ chạy và lắng nghe
host = 'localhost'
port = 4000

def abridgedPrint(data = b"", leadingArrow = True):
	if leadingArrow:
		console.print("--> :", style="bold cyan", end="")
		
	if len(data) > 1200:
		data = data[:1200] + b"..."
		
	try:
		console.print(f"{data.decode()}\n", style="bold cyan")
	except:
		try:
			console.print(data.encode("ISO-8859-1") + "\n", style="bold cyan")
		except: 
			print(f"{data}\n")

def getConfig():
	fileConfig = open('config.mèo')
	configs = json.load(fileConfig)
	return configs['cache_time'], configs['time_out'], configs['whitelisting'], configs['time'], configs['ext_to_save']
cache_time, time_out, whitelisting, allowed_time, ext_to_save = getConfig()

def createFile(fileName, content):
	# Neu extension cua file khong nam trong ext_to_save -> Khong luu cache
	if not (fileName[-3:] == "all" or fileName[-3:] in ext_to_save or fileName[-4:] in ext_to_save):
		return
	
	try:
		console.print(f"Creating {os.path.dirname(fileName)}", style="purple4")
		
		# Neu folder khong ton tai -> tao folder
		os.makedirs(os.path.dirname(fileName), exist_ok=True)
		
		# Ghi file
		with open(fileName + ".header", "wb") as f:
			f.write(content.partition(b"\r\n\r\n")[0])
		with open(fileName, "wb") as f:
			f.write(content.partition(b"\r\n\r\n")[2])
	except:
		console.print("Wrong file path", style="red bold")
	

def getRequestInfo(clientRequest):
	# Tach request cua Client tai moi dau cach, tao thanh mot mang chua cac thong tin
	try:
		requestList = clientRequest.decode("ISO-8859-1").split()
	# Neu khong the tach duoc -> Ket thuc ham
	except:
		console.print("Contains gzip")
		return	
	
	# Tim vi tri bat dau va ket thuc cua host, ie. Host: info.cern.ch
	hostStartIndex = clientRequest.decode("ISO-8859-1", "ignore").find("Host: ") + 6
	hostEndIndex = clientRequest.decode("ISO-8859-1", "ignore").find("\r\n", hostStartIndex)
	
	# Cac bien de tra ve
	method = requestList[0]
	resource = requestList[1]
	host = clientRequest.decode("ISO-8859-1", "ignore")[hostStartIndex: hostEndIndex]
	
	if resource[len(resource) - 1] == "/":
		resource = resource[:len(resource) - 1]
	
	# console.print(f"verb: {method}, resource: {resource}, host: {host}")
	
	return method, resource, host
	
def checkCache(msg):
	method, url, host = getRequestInfo(msg)
	
	# Tao ten file de luu cache
	# Xoa http://
	name = url.replace("http://", "")
	
	# Neu ten Resource khac ten Host -> them Resource o cuoi duong dan
	if host != name:
		fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, name)
		# fullPathName = c:/Users/phkhng/Documents/Code/socket-programming/cache/oosc.online/img/thing.png
	# Neu giong nhau -> them index o cuoi duong dan
	else:
		fullPathName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/", host, "index")
		# fullPathName = c:/Users/phkhng/Documents/Code/socket-programming/cache/oosc.online/index
		
	fullPathName = fullPathName.replace("\\", "/")
	
	data = b""
	isExist = True
	if not os.path.isfile(fullPathName):
		# console.print(f"No cache", style="deep_pink3")
		isExist = False
	else:
		fileInfo = datetime.datetime.fromtimestamp(os.path.getmtime(fullPathName))
		if (datetime.datetime.today().timestamp() - fileInfo.timestamp() > cache_time):
			return "", fullPathName, False
		
		console.print(f"Taking from cache: {fullPathName}", style="deep_pink3")
		with open(fullPathName + ".header", "rb") as fp:
			data = fp.read()
		with open(fullPathName, "rb") as pic:
			data += b"\r\n\r\n" + pic.read()
	
	return data, fullPathName, isExist

def proxy(msg):
	method, url, host = getRequestInfo(msg)
	
	cache, fullPathName, isExist = checkCache(msg)
	
	if (isExist):
		abridgedPrint(cache)
		return cache

	# console.print(f"Get fresh source", style="deep_pink3")
	hostPage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	hostPage.settimeout(time_out)
	# Thu ket noi web server: Ket noi thanh cong -> Gui sendMsg toi server va nhan ket qua vao data
	try:
		# Ket noi toi web server
		hostPage.connect((host, 80))
		
		if (method == "GET" or method == "HEAD"):
			sendMsg = f"{method} {url} HTTP/1.1\r\n"\
						"Host: " + host + "\r\n"\
						"Connection: close\r\n\r\n"
		elif (method == "POST"):
			if (msg.decode("utf-8", "ignore").partition("\r\n\r\n")[0].find("Connection:") != -1):
				sendMsg = f"{method} {url} HTTP/1.1\r\n"
				sendMsg += msg.decode("utf-8", "ignore").partition("\r\n")[2]
				sendMsg = sendMsg[:sendMsg.find("Connection:")] + "Connection: close" + sendMsg[sendMsg.find("\r\n", sendMsg.find("Connection:")):]
			else:
				sendMsg = f"{method} {url} HTTP/1.1\r\n"
				sendMsg += msg.decode("utf-8", "ignore").partition("\r\n")[2]
				sendMsg.replace(b"\r\n\r\n", b"Connection: close\r\n\r\n")
				
		else:
			raise Exception("Unsupported Method: " + method)
		
		console.print(f"Sending: ", style="green")
		console.print(sendMsg)
		hostPage.send(sendMsg.encode())

		# Nhan ve ket qua server vao tung mau kich thuoc 4096 -> Gop lai thanh mot bai hoan chinh
		data = b""
		while True:
			chunk = hostPage.recv(4096)
			if len(chunk) == 0:     # No more data received, quitting
				break
			data = data + chunk
		
		createFile(fullPathName, data)
	
	# Ket noi khong thanh cong -> data = page (da tao tu truoc)
	except Exception as e:
		console.print(e, style="red")
		data = page.encode("ISO-8859-1")
	
	if (method == "HEAD"):
		data = data.partition(b"\r\n\r\n")[0]
	
	# In ra ket qua nhan ve tu web server
	console.print(f"Response: ", style="green")
	abridgedPrint(data)
		
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
		
		# In ra thong tin Client: thoi gian, dia chi IP
		console.print(str(datetime.datetime.now()) + " | Connect from " + str(addr), style="bold")
		
		# In request cua Client
		abridgedPrint(msg, False)
		
		# Kiem tra thoi gian truy cap
		if (allowed_time != ""):
			start = datetime.time(int(allowed_time.partition("-")[0]), 0)
			end = datetime.time(int(allowed_time.partition("-")[2]), 0)
			if not (start <= datetime.datetime.today().time() <= end):
				console.print("Not in allowed time", style="red")
				client.send(page.encode())
				client.close()
				return
		
		method, url, host = getRequestInfo(msg)
		
		# Kiem tra ten mien truy cap
		if len(whitelisting) > 0 and not (host in whitelisting):
			console.print("Client must not access this domain: " + host, style="red")
			client.send(page.encode())
			client.close()
			return
			
		console.print(f"Method: {method}")
		pageSrc = proxy(msg)
		# Gui ket qua cua web server ve lai Client
		console.print("Bytes sent: ", client.send(pageSrc))
			
		client.close()
			
def main():
	print(f"cache_time: {cache_time}, whitelisting: {whitelisting}, time: {allowed_time}")
	
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