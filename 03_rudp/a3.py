# Here is the starting point for your Assignment 03 definitions. Add the 
# appropriate comment header as defined in the code formatting guidelines

import struct
import socket
import logging as log
import time
from hashlib import md5
from random import randint
from os import fstat

class Rudp():

    signature = "eWEwZ3VhbmcK"

    def __init__(self, p:str = '12345', h:str = "127.0.0.1"):
        """Initialize the object and create a socket. p, h are server's parameter
        
        Keyword Arguments:
            p {str} -- port number (default: {'12345'})
            h {str} -- host ip address (default: {"127.0.0.1"})
        """
        self.port = p
        h = socket.gethostbyname(h)
        self.host = h
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq = randint(0, 65535)

    def seqPlusOne(self):
        self.seq = Rudp.plusOne(self.seq, Rudp.Packet.seqL)

    @staticmethod
    def ackPlusOne(num):
        ack = Rudp.plusOne(num, Rudp.Packet.ackL)
        return ack

    @staticmethod
    def getFileSize(f):
        return fstat(f.fileno()).st_size

    @staticmethod
    def plusOne(num, length):
        bits = length * 8
        mod = 2 ** bits
        return (num + 1) % mod

    class WrongClient(Exception):
        pass

    class InvalidPacket(Exception):
        pass

    class Packet:
        """define the format of a rudp frame and the (max)length of each field
        """
        # header fields, length in bytes
        # checksum: MD5 hash of data
        checksumL = 16
        # sequence number: 16 bit int
        seqL = 2
        # # ACK or NACK
        # aOrNL = 1
        ackL = 2
        lengthL = 2

        # max length of payload in bytes
        payloadMax = 2000

        def __init__(self, sequence:int, acknowledge:int, data = b'\x00'):
            self.payload = data
            self.seq = sequence
            # self.aOrN = aN
            self.ack = acknowledge
            self.payload = data
            self.timesamp = None
            # status: Ture for live, False for dead
            self.status = True

        def construct(self):
            length = len(self.payload)
            headerWOchecksum = struct.pack('HHH', self.seq, self.ack, length)
            print("header: ", headerWOchecksum)
            packetWOchecksum = headerWOchecksum + self.payload
            checksum = md5(packetWOchecksum)
            checksum = checksum.digest()
            frame = checksum + packetWOchecksum
            return frame

        @property
        def length(self):
            return len(self.payload)

        @staticmethod
        def buffer() -> int:
            """return buffer size for a packet in bytes
            
            Returns:
                int -- buffer size required for RUDP packet
            """
            result = Rudp.Packet.header() + Rudp.Packet.payloadMax
            return result

        @staticmethod
        def header() -> int:
            """return required space for header in bytes
            
            Returns:
                int -- size of header
            """
            result = Rudp.Packet.checksumL + Rudp.Packet.seqL + Rudp.Packet.ackL + Rudp.Packet.lengthL
            return result

        @staticmethod
        def pack(sequence, acknowledge, data = b'\x00'):
            tempPacket = Rudp.Packet(sequence, acknowledge, data)
            return tempPacket.construct()
        
        @staticmethod
        def unpack(data) -> tuple:
            validity = False
            checksum = data[:Rudp.Packet.checksumL]
            packetWOchecksum = data[Rudp.Packet.checksumL:]
            structSeqAckLen = data[Rudp.Packet.checksumL: Rudp.Packet.header()]
            payload = data[Rudp.Packet.header():]

            check = md5(packetWOchecksum)
            if(check.digest() == checksum):
                validity = True
            
            (sequence, acknowledge, length) = struct.unpack("HHH", structSeqAckLen)
            frame = Rudp.Packet(sequence, acknowledge, payload)

            return (frame, validity)


