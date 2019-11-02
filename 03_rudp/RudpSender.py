from a3 import Rudp
from time import time
import logging as log
import socket
from os import fstat

class RudpSender(Rudp):
    timeout = 0.3

    def __init__(self, port, host):
        Rudp.__init__(self, port, host)
        self.server = (self.host, self.port)
        self.socket.settimeout(RudpSender.timeout)
    
    def sendFile(self, f):
        size = Rudp.getFileSize(f)
        log.info("File Size: " + str(size))

        self.stopAndWaitSend(Rudp.signature.encode())
        self.stopAndWaitSend(str(size).encode())

        while True:
            data = self.__readNext(f)
            if data:
                self.stopAndWaitSend(data)
            else:
                break

    def __readNext(self, f):
        try:
            fBuffer = f.read(Rudp.Packet.payloadMax)
        except Exception as e:
            print("Exception when reading file ", f, ". Because:", format(e))
        return fBuffer

    def stopAndWaitSend(self, data):
        packetSent = self.send(data)
        log.info("Packet: " + str(packetSent.seq) + " sent. Length: " + str(packetSent.length))
        ack = None
        while not (ack == packetSent.seq):
            try:
                ack = self.acknowledge()
            except socket.timeout:
                pass
            finally:
                if(ack is None) or (ack != packetSent.seq):
                    self.sendPacket(packetSent)
                    log.info("Packet resent")
                else:
                    log.info("Packet: " + str(packetSent.seq) + " ACKed")
                    break
            
    
    def send(self, data):
        packet = Rudp.Packet(self.seq, 0, data)
        packet.timesamp = time()
        self.sendPacket(packet)
        self.seqPlusOne()
        return(packet)

    def sendPacket(self, packet:Rudp.Packet):
        frame = packet.construct()
        self.socket.sendto(frame, self.server)

    @staticmethod
    def checkAck(packet: Rudp.Packet, ack: int):
        pass

    def acknowledge(self, validity = True):
        (data, s) = self.socket.recvfrom(Rudp.Packet.buffer())
        (packet, validity) = Rudp.Packet.unpack(data)
        if(validity and s == self.server):
            return packet.ack
        else:
            return None
        