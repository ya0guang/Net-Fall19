# Here is the starting point for your Assignment 02 definitions. Add the
# appropriate comment header as defined in the code formatting guidelines

import os
from ClientThread import *

def clientStart(host: str, port: str = '12345', udp: bool = False):
    """start a client. the server will be decided by socket(host, port),
    and the connection will be TCP if not specified to use UDP
    
    Arguments:
        host {str} -- server's host name
    
    Keyword Arguments:
        port {str} -- server's port number (default: {'12345'})
        udp {bool} -- wether to use UDP connection (default: {False})
    """

    # create the client socket according to the '-u' option
    if udp:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server info
    host = socket.gethostbyname(host)
    serverAddr = (host, port)

    # try to establish connection if using TCP
    if not udp:
        try:
            client.connect(serverAddr)
        except Exception as e:
            print("Could not connect server :", host,
                "port:", port, ", because", format(e))
            exit(1)
        finally:
            log.info("Connect to server %s success!", host)
    

    while True:
        # get input from the terminal
        msg = input(">").strip() + TERMINATOR

        # send msg to the server
        if udp:
            client.sendto(msg.encode(), serverAddr)
        else:
            client.send(msg.encode())

        # recv response from the server
        try:
            response = client.recv(BUFFER).decode()
        except Exception as e:
            print("Got exception: ", format(e), " while receiving message from server")
        finally:
            # if TCP socket received zero-length response
            if len(response) == 0:
                sys.exit()
            log.info("Server says: %s", response)

        if msg.strip() is "exit" or "goodbye":
            if not udp:
                client.close()
            sys.exit()

def serverStart(port: str = '12345', udp: bool = False):

    if udp:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # host = socket.gethostname()
    host = "127.0.0.1"

    try:
        server.bind((host, port))
    except Exception as e:
        print("Could not bind port: ", port, ", because", format(e))
        exit(1)

    log.info("Service is on! hostname: %s, port: %s", host, port)
    log.info("Service is using UDP: %r", udp)

    if not udp: server.listen(10) 
    clientThreads = {}

    while True:

        # in UDP case, the server will handle message receiving and put it to the queue corresponding to
        # the client, or create a new client thread if there is no corresponding client
        if udp:
            (msg, clientAddr) = server.recvfrom(BUFFER)
            if len(msg) > 0:
                if clientAddr in clientThreads:
                    clientThreads[clientAddr].inQueue.put(msg)
                else:
                    clientThreads[clientAddr] = (UDPThread(msg, clientAddr, server))
                    clientThreads[clientAddr].start()
        # in TCP case, the server will wait for incoming connection continuesly and deliever it to a
        # new thread after accepting a new connection. the thread will handle everything
        else:
            try:
                server.settimeout(1)
                (clientSocket, clientAddr) = server.accept()
                clientThreads[clientAddr] = TCPThread(clientAddr, server, clientSocket)
                clientThreads[clientAddr].start()
            except socket.timeout:
                pass

        # check if there is a thread is not alive, or if any client has sent "exit" command
        clientToAbort = None
        for (clientAddr, clientThread) in clientThreads.items():
            if clientThread.exitFlag:
                log.info("Got an exit signal, terminating myself...")
                server.close()
                sys.exit()
            if not clientThread.is_alive():
                clientToAbort = clientAddr

        # kick the client(dead thread) off our threads dictionary
        if clientToAbort:
            del clientThreads[clientToAbort]
            log.info("%s has left.", clientToAbort)
