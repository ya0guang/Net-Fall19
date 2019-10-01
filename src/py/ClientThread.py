import socket
import threading
import sys
import logging as log
import queue
import socket
import sys

BUFFER = 256
TERMINATOR = '\n'


class ClientThread(threading.Thread):
    """father class for TCP and UDB thread class"""

    def __init__(self, addr: tuple, server: socket.socket):
        threading.Thread.__init__(self)
        self.serverSocket = server
        self.clientIdentifier = addr
        # if exitProcess is true, then the server program will be killed after cleaning jobs
        self.exitFlag = False
        log.info("New Thread for: %s", self.clientIdentifier)


class TCPThread(ClientThread):
    def __init__(self, addr: tuple, server: socket.socket, client: socket.socket):
        ClientThread.__init__(self, addr, server)
        self.clientSocket = client

    def run(self):
        # after received "hello" from the client, this will turn to be True.
        # if this value turn to be False, then the server will close the connection
        available = False

        while True:
            try:
                msg = self.clientSocket.recv(BUFFER).decode()
            except Exception as e:
                print("Got exception:", format(
                    e), ", while receiving message from client: ", self.clientIdentifier)
            finally:
                # msg is zero length or EOF: connection is closed unexpectedly
                if(len(msg) == 0):
                    log.warn("Connection closed by the client: %s",
                             self.clientIdentifier)
                    available = False
                else:
                    log.info("New message from %s: %s",
                             self.clientIdentifier, msg)

            available, self.exitFlag, response = protocol(available, msg)

            # send the response to the client
            self.clientSocket.send(response.encode())

            # cleaning jobs: close the client socket and jump out
            if (not available) or self.exitFlag:
                self.clientSocket.close()
                break


class UDPThread(ClientThread):
    def __init__(self, firstMessage: bytes, addr: tuple, server: socket):
        ClientThread.__init__(self, addr, server)
        # use a queue to pass incoming new message
        self.inQueue = queue.Queue()
        self.inQueue.put(firstMessage)

    def run(self):
        available = False

        while True:
            msg = self.inQueue.get().decode()
            log.info("Got a new message from UDP client %s: %s",
                     self.clientIdentifier, msg)
            available, self.exitFlag, response = protocol(available, msg)
            self.serverSocket.sendto(response.encode(), self.clientIdentifier)

            if (not available) or self.exitFlag:
                break


def protocol(available: bool, msg: str) -> (bool, bool, str):
    """realize the protocol described in the assignment.
    from the current availibility state and the incoming message, the server will 
    generate control flag and the response

    the protocol will run just like the SMTP protol, waiting for message and operate control commands
    only after the client says "Hello"

    Arguments:
        available {bool} -- current availability of the client socket
        msg {str} -- msg received from client, length should not be zero

    Returns:
        (newAvaliable[bool], exitFlag[bool], response[str])
    """
    # status is the new available to be returned
    status = available
    exitFlag = False
    # normal functions available only after received "hello"
    if available == True:
        if msg.strip() == "exit":
            status = False
            exitFlag = True
            response = "ok"
        elif msg.strip() == "goodbye":
            status = False
            response = "farewell"
        else:
            response = msg
    else:
        # receive "hello" from the client to activate the program
        if msg.strip() == "hello":
            status = True
            response = "world"

        if status == False:
            response = "polite computer will say hello first"

    return (status, exitFlag, response + TERMINATOR)
