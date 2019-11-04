from a3 import Rudp
from time import time
import logging as log
import socket
from os import fstat
from queue import Queue
from enum import Enum
from math import ceil

class RudpSender(Rudp):
    # timeout for sending packet(s) in second
    timeout = 0.3
    # for go-back-N algorithm, N = sendWindow
    sendWindow = 1
    threshHold = None

    def __init__(self, port:int, host:str):
        """initialize sender (client)
        
        Arguments:
            port {int} -- port number of the server(receiver)
            host {str} -- hostnamse of the server
        """
        Rudp.__init__(self, port, host)
        self.server = (self.host, self.port)
        self.socket.settimeout(RudpSender.timeout)

    def goBackNSend(self, f):
        """GBN file sending method
        
        Arguments:
            f {file} -- (opened) readable binary file
        """
        size = Rudp.getFileSize(f)
        log.info("File Size: " + str(size))

        self.stopAndWaitSendData(Rudp.signature.encode())
        self.stopAndWaitSendData(str(size).encode())

        # a list holding on-flight packets
        sendList = []
        # indicates the end of file
        readEnd = False
        # store recent acks for congestion control
        ackList = []

        while (not readEnd) or (len(sendList)):
            # fill sendList
            packetToFill = RudpSender.sendWindow - len(sendList)
            if packetToFill > 0:
                for i in range(packetToFill):
                    data = self.__readNext(f)
                    if data:
                        p = self.send(data)
                        print("Packet Seq: ", p.seq, " Added to Send List")
                        sendList.append(p)
                    else:
                        readEnd = True
            # try to receive ack
            try: 
                while len(sendList):
                    ack = self.acknowledge()
                    print("Ack Received: ", ack)
                    self.mark(sendList, ack)
                    ackList.append(ack)
                    self.checkDupAcks(ackList)
                    sendList = Rudp.cleanPacketList(sendList)
            except socket.timeout:
                print("Timeout")
                self.resendPackets(sendList)
                self.congestionControl(RudpSender.LossEvent.Timeout)
            except RudpSender.DupAcks:
                print("Dupacks")
                ackList = []
                self.resendPackets(sendList)
                self.congestionControl(RudpSender.LossEvent.DupAcks)
            else:
                self.congestionControl(RudpSender.LossEvent.NoLoss)

    def mark(self, packets: list, ack:int):
        """mark the status of an acked packet as False(unlive)
        
        Arguments:
            packets {Rudp.Packet} -- a list of packets
            ack {int} -- received ack number
        """
        for p in packets:
            p.status = not (ack >= p.seq)

    def resendPackets(self, packets: list)-> int:
        """GBN resend when packet loss detected
        
        Arguments:
            packets {list} -- packets to resend
        
        Returns:
            int -- number of resent packets
        """
        log.info("Resending triggered")
        for packet in packets:
            self.sendPacket(packet)
            print(packet.seq, end=" ")
        print()
        return len(packets)

    def stopAndWaitSend(self, f):
        """stop-and-wait file sending method 
        
        Arguments:
            f {file} -- (opened) readable binary file to send
        """
        size = Rudp.getFileSize(f)
        log.info("File Size: " + str(size))

        self.stopAndWaitSendData(Rudp.signature.encode())
        self.stopAndWaitSendData(str(size).encode())

        while True:
            data = self.__readNext(f)
            if data:
                self.stopAndWaitSendData(data)
            else:
                break

    def __readNext(self, f) -> bytes:
        """read file and return next N bits. N is set in Rudp.Packet.PayloadMax
        
        Arguments:
            f {file} -- file to send
        
        Returns:
            bytes -- next part of file for sending in bytes
        """
        try:
            fBuffer = f.read(Rudp.Packet.payloadMax)
        except Exception as e:
            print("Exception when reading file ", f, ". Because:", format(e))
        return fBuffer

    def stopAndWaitSendData(self, data:bytes):
        """wrap the packet, send data to the server and wait for an ack
        
        Arguments:
            data {bytes} -- data to send
        """
        
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
            
    def send(self, data:bytes):
        """warp a packet for data and send this
        
        Arguments:
            data {bytes} -- data to send
        """
        packet = Rudp.Packet(self.seq, 0, data)
        packet.timesamp = time()
        self.sendPacket(packet)
        self.seqPlusOne()
        return(packet)

    def sendPacket(self, packet:Rudp.Packet):
        """send a Rudp.Packet
        
        Arguments:
            packet {Rudp.Packet} -- packet for sending 
        """
        frame = packet.construct()
        self.socket.sendto(frame, self.server)

    @staticmethod
    def checkDupAcks(ackList: list):
        if len(ackList) > 3:
            ackList = ackList[-3:]
            if (ackList[0] == ackList [1] == ackList[2]) :
                raise RudpSender.DupAcks("Three Duplicated Acks of" + str(ackList[0]))

    def acknowledge(self, validity = True) -> int:
        """receive an Rudp.packet and get ack# of the packet
        
        Keyword Arguments:
            validity {bool} -- the validity of this packet (default: {True})
        
        Returns:
            int -- ack#
        """
        (data, s) = self.socket.recvfrom(Rudp.Packet.buffer())
        (packet, validity) = Rudp.Packet.unpack(data)
        if(validity and s == self.server):
            return packet.ack
        else:
            return None
    
    def congestionControl(self, lossType):
        if(lossType == RudpSender.LossEvent.NoLoss):
            # Slow Start Phase
            if RudpSender.threshHold == None or RudpSender.sendWindow < RudpSender.threshHold:
                RudpSender.sendWindow *= 2
            # Conjestion Avoidance Phase
            else:
                RudpSender.sendWindow += 1
        elif RudpSender.threshHold == None:
            RudpSender.threshHold = RudpSender.sendWindow
            return
        
        if(lossType == RudpSender.LossEvent.Timeout):
            RudpSender.threshHold = ceil(RudpSender.sendWindow / 2)
            RudpSender.sendWindow = 1
        if(lossType == RudpSender.LossEvent.DupAcks):
            RudpSender.threshHold = ceil(RudpSender.sendWindow / 2)
            RudpSender.sendWindow = RudpSender.threshHold
        
        print("Window Size: ", RudpSender.sendWindow, "Threshold: ", RudpSender.threshHold)


    class LossEvent(Enum):
        NoLoss = 0
        Timeout = 1
        DupAcks = 2

    class DupAcks(Exception):
        pass