from a3 import Rudp
import logging as log
import socket

class RudpReceiver(Rudp):
    def __init__(self, port:int):
        """initialize receiver
        
        Arguments:
            port {int} -- port number to bind on local server
        """
        Rudp.__init__(self, p = port)
        self.client = None
        self.ack = None
        # for testing on server
        self.host = "10.10.2.10"
        # for local test
        # self.host = "127.0.0.1"
        # host = socket.gethostname()
        # self.host = socket.gethostbyname(host)
        try:
            print(self.host, self.port)
            self.socket.bind((self.host, self.port))
        except Exception as e:
            print("Cannot bind port: ", self.port, ". Because:", format(e))

    def goBackNRecv(self, f):
        """GBN file receiving method
        
        Arguments:
            f {_io.TextIOWrapper} -- (opened) file to write
        """
        self.listen()
        size = self.getSize()

        # cache for incoming packets
        recvList = []

        while True:
            try:
                recvPacket = self.recvPacket()
                print("Packet Seq: ", recvPacket.seq, " Received")
                recvList = self.insertOrderedPacket(recvPacket, recvList)
            except (Rudp.InvalidPacket, Rudp.WrongClient):
                pass
            # ack consecutive packets and write to file
            for packet in recvList:
                if packet.seq == Rudp.ackPlusOne(self.ack):
                    self.acknowledge(packet.seq)
                    self.ack = Rudp.ackPlusOne(self.ack)
                    f.write(packet.payload)
                    f.flush()
                    packet.status = False
                    print("Packet Seq: ", packet.seq, " Acked and Written")
                else:
                    self.acknowledge(self.ack)
            if not len(recvList):
                self.acknowledge(self.ack)

            # drop acked files
            self.cleanPacketList(recvList)

            if Rudp.getFileSize(f) == size:
                f.close()
                log.info("Transmission Complete, exit...")
                break

    def insertOrderedPacket(self, packet:Rudp.Packet, packets:list) -> list:
        """insert packet to the received packet list presisting the sequence # order
        
        Arguments:
            packet {Rudp.Packet} -- received packet
            packets {list} -- received packets list
        
        Returns:
            list -- new list after inserting
        """
        i = 0
        for i in range(len(packets)):
            if packets[i].seq == packet.seq:
                print("Received Duplicated Packet, dropped: ", packet.seq)
                return packets
            if packets[i].seq > packet.seq:
                break

        if packet.seq <= self.ack:
            print("Packet Seq: ", packet.seq, " Dropped")
            return packets
        else:
            result = packets[:i] + [packet] + packets[i:]
            return result

    def stopAndWaitRecv(self, f):
        """stop-and-wait file receiving method
        
        Arguments:
            f {_io.TextIOWrapper} -- (opened) file to save
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
    
    def cleanPacketList(self, packets: list) -> list:
        result = Rudp.cleanPacketList(packets)
        for p in result:
            if p.seq <= self.ack:
                result.remove(p)
        return result


    def getSize(self):
        size = None
        while not size:
            try:
                rawData = self.recvData()
                size = int(rawData.decode())
            except Exception:
                pass
        return size

    def recvPacket(self) -> Rudp.Packet:
        """receive a valid packet from the client
        
        Raises:
            Rudp.WrongClient: the address of the client doesn't corresponds to self.client
        
        Returns:
            Rudp.Packet -- received packet
        """
        (packet, validity, c) = self.recv()
        if(c != self.client):
            raise Rudp.WrongClient("Wrong Package from " + c)
        return packet

    def recvData(self) -> bytes:
        """receive from socket and return the content and acknowledge the packet
        used in stop and wait
        
        Returns:
            bytes -- Rudp.Packet.payload
        """
        
        packet = self.recvPacket()
        if(packet.seq == Rudp.ackPlusOne(self.ack)):
            self.ack = Rudp.ackPlusOne(self.ack)
            self.acknowledgePacket(packet)
            return packet.payload
        else:
            return None

    def recv(self) -> tuple:
        """receive raw data from socket and check the validity by checksum
        
        Raises:
            Rudp.InvalidPacket: checksum doesn't match the packet's data
        
        Returns:
            tuple -- (Rudp.Packet, validity: bool, client:(ip addr, port))
        """
        (data, c) = self.socket.recvfrom(Rudp.Packet.buffer())
        # print(data)
        (packet, validity) = Rudp.Packet.unpack(data)
        if(validity):
            print("Valid Packet Received From: ", c)
        else:
            raise Rudp.InvalidPacket("Invalid Packet Received")

        return (packet, validity, c)

    def acknowledgePacket(self, packet: Rudp.Packet):
        """send packet acknowledge received valid packet
        
        Arguments:
            packet {Rudp.Packet} -- packet received
        """
        self.acknowledge(packet.seq)

    def acknowledge(self, sequence: int):
        """send packet acknowledging a sequence number to the client
        
        Arguments:
            sequence {int} -- sequence #
        """
        ackPacket = Rudp.Packet(self.seq, sequence)
        frame = ackPacket.construct()
        self.seqPlusOne()
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
                print(frame.payload)
            except Exception as e:
                print(format(e))
            if (frame.payload.decode() == Rudp.signature) and validity:
                self.client = c
                self.ack = frame.seq
                self.acknowledgePacket(frame)
                break
        return True

