# Here is the starting point for your Assignment 02 definitions. Add the
# appropriate comment header as defined in the code formatting guidelines

import socket
import sys
import os
import logging as log
import threading

BUFFER = 256
TERMINATOR = '\n'


def serverStart(port: str = '12345', udp: bool = False):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host = socket.gethostname()
    host = "127.0.0.1"

    try:
        server.bind((host, port))
    except Exception as e:
        print("Could not bind port: ", port, ", because", format(e))
        exit(1)

    log.info("Service is on! hostname: %s, port: %s", host, port)

    server.listen(10)
    clientThreads = []

    while True:

        (clientSocket, clientAddr) = server.accept()
        clientThreads.append(ClientThread(clientAddr, server, clientSocket))
        clientThreads[-1].start()


def clientStart(host: str, port: str = '12345', udp: bool = False):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = socket.gethostbyname(host)

    # try to establish connection
    try:
        client.connect((host, port))
    except Exception as e:
        print("Could not connect server :", host,
              "port:", port, ", because", format(e))
        exit(1)

    log.info("Connect to server %s success!", host)

    while True:
        msg = input(">").strip() + TERMINATOR
        client.send(msg.encode())

        try:
            response = client.recv(BUFFER).decode()
        except Exception as e:
            print("Got exception: ", format(e), " while receiving message from server")
        finally:
            if len(response) == 0:
                sys.exit()

        log.info("Server says: %s", response)


class ClientThread(threading.Thread):

    def __init__(self, addr: tuple, server: socket.socket, client: socket.socket):
        threading.Thread.__init__(self)
        self.serverSocket = server
        self.clientSocket = client
        self.clientIdentifier = addr
        log.info("Incoming connect from: %s", self.clientIdentifier)

    def run(self):
        # after received "hello" from the client, this will turn to be True. if this value turn to be False, then the server will close the connection
        available = False
        # if exitProcess is true, then the server program will be killed after cleaning jobs
        exitProcess = False

        while True:

            try:
                msg = self.clientSocket.recv(BUFFER).decode()
            except Exception as e:
                print("Got exception:", format(e), ", while receiving message from client: ", self.clientIdentifier)
            finally:
                # msg is zero length or EOF: connection is closed unexpectedly
                if(len(msg) == 0):
                    log.warn("Connection closed by the client: %s", self.clientIdentifier)
                    available = False
                else:
                    log.info("New message from %s: %s", self.clientIdentifier, msg)

            # normal functions available only after received "hello"
            if available == True:
                if msg.strip() == "exit":
                    available = False
                    exitProcess = True
                    response = "ok" + TERMINATOR
                elif msg.strip() == "goodbye":
                    available = False
                    response = "farewell" + TERMINATOR
                else:
                    response = msg
            else:
                # receive "hello" from the client to activate the program
                if msg.strip() == "hello":
                    available = True
                    response = "world" + TERMINATOR

                if available == False:
                    response = "polite computer will say hello first" + TERMINATOR

            # send the response to the client
            self.clientSocket.send(response.encode())

            # cleaning jobs: close the client socket and jump out
            if not available:
                self.clientSocket.close()
                break

            # cleaning jobs: close both server and client sockets and terminate the program
            if exitProcess:
                self.serverSocket.close()
                self.clientSocket.close()
                os._exit()
