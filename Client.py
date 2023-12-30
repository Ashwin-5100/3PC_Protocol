import socket
import time
import sys

HOST = "127.0.0.1"
PORT = 49152 + int(sys.argv[1]) -1


def Client():
	s = socket.socket()		
	s.connect((HOST, PORT))

	print("\nConnected to Transaction Manager, Ready to recieve Query.\n")
	# receive data from the server
	query = s.recv(1024).decode()
	print("Query Recieved ... What do you want to do with it:- ")
	print("1. Process it\n2. Cannot Process it\n3. Ignore it (For Visualizing Fault)\n")
	switch = input("Your Choice : ")
	print("\n")
	if (switch == '1'):
		print("Query recieved :- {}".format(query))
		print("Processing Query ...")
		result = eval(query)
		s.send("Yes".encode())
		s.send(str(result).encode())
		time.sleep(1)
		print("Query Processed !")
	elif (switch == '2'):
		print("Sending negative acknowledgement to Transaction Manager.")
		s.send("No".encode())
	else :
		print("Not responding to Transaction Manager ... Simulating faulty node.")
		s.send("Wait".encode())
	s.close()

	while True:
		s = socket.socket()
		s.connect((HOST,PORT))
		response = s.recv(1024).decode()
		if (response == "Abort"):
			print("Abort Message recieved from transaction manager, Aborting Transaction ...\n")
			s.close()
			break
		elif (response == "Commit"):
			print("\nPreCommit Message recieved from transaction manager, Commiting Transaction locally and sending acknowledgement to Transaction Manager...\n")
			s.send("Yes".encode())
			s.close()
			break
		else:
			query = response
			response = eval(query)
			print("\nAdditional query recieved to make up for faulty node :- {}".format(query))
			print("Processing Query ... ")
			time.sleep(2)
			print("Query Processed ! Sending result back to Transaction Manager ...")
			s.send(str(response).encode())
			s.close()




# Driver function
if __name__ == '__main__':
	# synchronize time using clock server
	Client()
