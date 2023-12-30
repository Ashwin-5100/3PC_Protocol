import socket
import time

HOST = "127.0.0.1"
PORT = 49152

def initiateServer():
    # Ports 49152-65535– These are used by client programs and you are free to use these in client programs.
    numClients = int(
        input("\nGive number of Slave nodes available for Transaction Manager:- "))
    sockets = []
    for i in range(numClients):
        s = socket.socket()
        sockets.append(s)
        sockets[i].bind((HOST, PORT+i))

    s = socket.socket()
    print("\nSockets successfully Created.")
    time.sleep(1)

    # Start listening to requests
    for i in range(numClients):
        sockets[i].listen(300)

    print("Sockets are listening ...")
    time.sleep(1)
    query_real = ""
    # Transaction Manager running forever ...
    while True:
        # Establish connection with client
        print("\nAvailable slave nodes are ready for use.\n")
        query = input("Input the query you want to run : ")
        query_real = query
        queryBroken = []
        for i in range(numClients):
            queryBroken.append("")
        st = ""
        index = 0
        for character in query:
            if (character == ' '):
                continue
            elif (character == '+' or character == '-'):
                queryBroken[index] = st
                index += 1
                st = ""
            else:
                st += character
        if (st != ""):
            queryBroken[index] = st
            index += 1
            st = ""
        st = ""
        # Debugging ...
        # for x in range(len(queryBroken)):
        #     print( queryBroken[x])
        Abort = False
        Commit = True
        responseValues = []
        for i in range(numClients):
            conn, address = sockets[i].accept()
            print('\nServer connected to', address,
                  'aka Client node', str(i+1))
            conn.send(queryBroken[i].encode())
            response = conn.recv(1024).decode()
            if (response == "Yes"):
                responseValues.append(conn.recv(1024).decode())
                print("Positive acknowledgement recieved from Client node " +
                      str(i+1) + ",\nValue recieved = " + responseValues[i])
                # st += responseValues[i]
                # st += " + "
                conn.send("Pre Commit".encode())
            elif (response == "No"):
                Abort = True
                Commit = False
                print("Negative acknowledgement recieved aborting transaction.")
                responseValues.append("Not Recieved")
                conn.send("Abort".encode())
            elif (response == "Wait"):
                Commit = False
                print("Waiting for response ... ")
                print(
                    "Response not recieved, waiting for some client node to be free to route this query to ...")
                responseValues.append("Fault")
            conn.close()

        if (Abort == False and Commit == False):
            for i in range(numClients):
                if (responseValues[i] == "Fault"):
                    print(
                        "\nFlooding all other client nodes for resolving faulty client node {}'s query...\n".format(i+1))
                    for k in range(numClients):
                        if (k == i):
                            continue
                        else:
                            conn, address = sockets[k].accept()
                            print(
                                "Client Node {} has accepted additional query request. Sending query of faulty node ...\n".format(k+1))
                            conn.send(queryBroken[i].encode())
                            responseValues[i] = conn.recv(1024).decode()
                            conn.close()
                            break
                    print(
                        "\nResponse recieved for query through other working node ... \n")

        if (Abort == True):
            j = 0
            for i in range(numClients):
                if (responseValues[i] == "Not Recieved"):
                    j = i
            print("\nNegative acknowledgement recieved from client node {}, sending abort message to all nodes.".format(j+1))
            for i in range(numClients):
                conn, address = sockets[i].accept()
                conn.send("Abort".encode())
                conn.close()
        else:  # Positive Ack Precommit
            print(
                "\nPositive acknowledgement recieved from all nodes sending PreCommit message to all nodes.")
            for i in range(numClients):
                conn, address = sockets[i].accept()
                conn.send("Commit".encode())
                ack = conn.recv(1024).decode()
                if (ack == "No"):
                    Abort = False
                conn.close()

        if (Abort == False):
            for i in range(numClients):
                st += responseValues[i]
                if (i != (numClients-1)):
                    st += ' + '
            st = query_real
            query = st
            print("\nPositive acknowledgement recieved for all the precommit messages, finally commiting the transaction ... ")
            print("Value of query at commit : " + str(eval(query_real)))
            print("\n")
        break


# Driver function
if __name__ == '__main__':
    # Trigger the Clock Server
    initiateServer()
