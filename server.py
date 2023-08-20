import socket 
import threading
import json
import os
from rich.console import Console
console = Console()
import datetime

with open("403.html", "r") as fp:
	page = fp.read()

# Định nghĩa host và port mà server sẽ chạy và lắng nghe
host = '127.0.0.1'
port = 8888

def abridgedPrint(data = b"", leadingArrow = True):
	if leadingArrow:
		console.print("--> :", style="bold cyan", end="")
		
	if len(data) > 2000:
		data = data[:2000] + b"..."
		
	try:
		console.print(f"{data.decode()}\n", style="bold cyan")
	except:
		try:
			console.print(data.decode("ISO-8859-1", "ignore") + "\n", style="bold cyan")
		except: 
			console.print(data.decode("ISO-8859-2", "ignore") + "\n", style="bold cyan")

def getConfig():
	fileConfig = open('config.json')
	configs = json.load(fileConfig)
	return configs['cache_time'], configs['time_out'], configs['whitelisting_enable'], configs['whitelisting'], configs['time_enable'], configs['time'], configs['ext_to_save']
cache_time, time_out, whitelisting_enable, whitelisting, time_enable, allowed_time, ext_to_save = getConfig()

def createFile(fileName, content):
	# Neu extension cua file khong nam trong ext_to_save -> Khong luu cache
	save = False
	for ext in ext_to_save:
		if fileName.find("." + ext) != -1:
			save = True
	
	if not save:
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
	special_characters=['@','#','$','*','&', '<', '>', '"', '|', '?', '=']
	for char in special_characters:
		fullPathName = fullPathName.replace(char, '_')
	
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
				sendMsg.replace(b"\r\n\r\n", b"\r\nConnection: close\r\n\r\n")
				
		else:
			raise Exception("Unsupported Method: " + method)
		
		console.print(f"Sending: ", style="green")
		console.print(sendMsg)
		hostPage.send(sendMsg.encode())

		# Lay phan head cua response
		data = b""
		while data.find(b"\r\n\r\n") != -1:
			data += hostPage.recv(1)
		
		# Lay tiep body cua response dua theo thong tin tu header
		# Neu response su dung chunked
		if (data.find(b"Transfer-Encoding:") != -1 and data.find(b"chunked", data.find(b"Transfer-Encoding:")) != -1):
			print("Chunked")
			length = b""
			while True:
				# Lay kich thuoc cho block du lieu tiep theo
				while True:
					length += hostPage.recv(1)
					if length.find(b"\r\n" != -1):
						break
				print(f"Size left: {sizeLeft}")
				sizeLeft = int(length.replace(b"\r\n", ""), 16)
				
				if sizeLeft <= 0:
					data += b"\r\n"
					break
				else:
					# Nhan phan goi tin con lai, append vao data
					chunk = b""
					while sizeLeft > 0:
						chunk = hostPage.recv(min(sizeLeft, 4096)) + b"\r\n"
						sizeLeft -= len(chunk)
						data += chunk
				
			
		# Neu response su dung content lenght -> lay kich thuoc tu Content-length va nhan goi tin ve cho den khi het kich thuoc do
		elif (data.find(b"Content-Length:") != -1):
			print("Content length")
			sizeLeft = data.partition(b"Content-Length:")[2].partition(b"\r\n")
			sizeLeft = int(sizeLeft, 16)
			print(f"Size left: {sizeLeft}")
			
			while sizeLeft > 0:
				chunk = hostPage.recv(4096)
				data = data + chunk
				sizeLeft - len(chunk)
			
		# Neu response khong su dung nhung cach tren
		else:
			print("Normal")
			while True:
				chunk = hostPage.recv(4096)
				if len(chunk) == 0:     # No more data received, quitting
					break
				data = data + chunk
		
		createFile(fullPathName, data)
	
	# Ket noi khong thanh cong -> data = page (da tao tu truoc)
	except Exception as e:
		console.print(e, style="red")
		data = page.encode("ISO-8859-1", "ignore")
	
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
		if (time_enable):
			start = datetime.time(int(allowed_time.partition("-")[0]), 0)
			end = datetime.time(int(allowed_time.partition("-")[2]), 0)
			if not (start <= datetime.datetime.today().time() <= end):
				console.print("Not in allowed time", style="red")
				client.send(page.encode())
				client.close()
				return
		
		method, url, host = getRequestInfo(msg)
		
		# Kiem tra ten mien truy cap
		if whitelisting_enable and not (host in whitelisting):
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
	print(f"Caching Age: {cache_time}s; {'Whitelist: ' + ', '.join(whitelisting) + '; ' if (whitelisting_enable) else ''}{'Allowed time: ' + allowed_time if (time_enable) else ''}")
	
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host, port))

	server.listen(10)
	console.print("Server listening on port", port)


	while True:
		try:
			console.print("Waiting for new user", style="bold yellow")
			client, addr = server.accept()
			thread = threading.Thread(target = runTask, args = (client, addr))
			thread.start()
			# runTask(client, addr)
			
		except KeyboardInterrupt:
			console.print("Closing program")
			client.close()

		
if __name__ == "__main__":
	main()