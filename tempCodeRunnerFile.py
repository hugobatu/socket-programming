f sendMessage(clientRequest):
	requestList = clientRequest.decode().split()
	
	verb = requestList[0]
	
