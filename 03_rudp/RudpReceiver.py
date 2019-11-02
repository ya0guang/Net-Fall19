from a3 import Rudp
import logging as log

class RudpReceiver(Rudp):
    def __init__(self, port):
        Rudp.__init__(self, p = port)
        self.client = None
        self.ack = None

        try:
            print(self.host, self.port)
            self.socket.bind((self.host, self.port))
        except Exception as e:
            print("Cannot bind port: ", self.port, ". Because:", format(e))

    def stopAndWaitRecv(self, f):
        """accept an rudp connection if the client's signature is the same with the server's
        """
        self.listen()
        size = self.getSize()

        while True:
            try:
                data = self.recvData()
            except Exception as e:
                print(format(e))
            if data:
                f.write(data)
                f.flush()
                print("file size: ", Rudp.getFileSize(f))
            if Rudp.getFileSize(f) == size:
                f.close()
                log.info("Transmission Complete, exit...")
                break
    
    def getSize(self):
        size = None
        while not size:
            try:
                rawData = self.recvData()
                size = int(rawData.decode())
            except Exception:
                pass
        return size

    def recvData(self):
        (packet, validity, c) = self.recv()
        if(c != self.client):
            raise Rudp.WrongClient("Wrong Package from " + c)
        if(packet.seq == Rudp.ackPlusOne(self.ack)):
            self.ack = Rudp.ackPlusOne(self.ack)
            self.acknowledge(packet)
            return packet.payload
        else:
            return None

    def recv(self):
        (data, c) = self.socket.recvfrom(Rudp.Packet.buffer())
        (packet, validity) = Rudp.Packet.unpack(data)
        if(validity):
            print("Valid Packet Received From: ", c)
        else:
            raise Rudp.InvalidPacket("Invalid Packet Received")

        return (packet, validity, c)

    def acknowledge(self, packet: Rudp.Packet):
        """send packet acknowledge received valid packet
        
        Arguments:
            packet {Rudp.Packet} -- packet received
        """
        ackPacket = Rudp.Packet(self.seq, packet.seq)
        frame = ackPacket.construct()
        self.seq += 1
        self.socket.sendto(frame, self.client)

    def listen(self) -> bool:
        """like listen() in TCP: accept a client if receive a packet of Rudp.signature. 
        listen() will block the program
        
        Returns:
            bool -- Return true until a valid client is connected 
        """
        while True:
            try:
                (frame, validity, c) = self.recv()
            except Exception as e:
                print(format(e))
            if (frame.payload.decode() == Rudp.signature) and validity:
                self.client = c
                self.ack = frame.seq
                self.acknowledge(frame)
                break
        return True

