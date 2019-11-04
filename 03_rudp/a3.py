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

    # client and server will transmit signature first to ensure they are using the same version of RUDP protocol
    signature = "eWEwZ3VhbmcK"

    def __init__(self, p: int = 12345, h: str = "127.0.0.1"):
        """Initialize the object and create a socket. p, h are server's parameter

        Keyword Arguments:
            p {str} -- port number (default: {'12345'})
            h {str} -- host ip address (default: {"127.0.0.1"})
        """
        self.port = p
        h = socket.gethostbyname(h)
        self.host = h
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # generate the seq# randomly
        self.seq = randint(0, 65535)

    def seqPlusOne(self):
        """ helper function to inc seq by 1
        """
        self.seq = Rudp.plusOne(self.seq, Rudp.Packet.seqL)

    @staticmethod
    def ackPlusOne(num: int) -> int:
        """increase ack by one

        Arguments:
            num {int} -- usually ack#

        Returns:
            int -- increased ack#
        """
        ack = Rudp.plusOne(num, Rudp.Packet.ackL)
        return ack

    @staticmethod
    def getFileSize(f) -> int:
        """get the opened file size

        Arguments:
            f {file} -- opened file

        Returns:
            int -- size in byte
        """
        return fstat(f.fileno()).st_size

    @staticmethod
    def plusOne(num: int, length: int) -> int:
        """plus one on the num. if overflow happens, return 0
        
        Arguments:
            num {int} -- number to be increased
            length {int} -- length in bytes of num
        
        Returns:
            int -- increased num
        """

        bits = length * 8
        mod = 2 ** bits
        return (num + 1) % mod

    @staticmethod
    def cleanPacketList(packets:list) -> list:
        """accept a list of packets and kick off consecutive dead packets(Packet.status == False) from the beginning
        for RudpSender, "dead" means the packet has been acked
        for RudpReceiver, "dead" means the content of this packet has been written to disk
        
        Arguments:
            packets {list} -- a list of packets to be searched
        
        Returns:
            list -- cleaned packets list
        """
        while len(packets):
            print("Packets list Length: ", len(packets))
            if not packets[0].status:
                packets.pop(0)
            else:
                break
        return packets

    class WrongClient(Exception):
        """If received message from a host other than current, raise this exception
        """
        pass

    class InvalidPacket(Exception):
        """if the checksum is not in accord with the content(not integrate), raise this exception
        """
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

        # max length of payload(data) in bytes
        payloadMax = 2000

        def __init__(self, sequence: int, acknowledge: int, data=b'\x00'):
            """initialize a Packet
            
            Arguments:
                sequence {int} -- sequence #, a.k.a seq field
                acknowledge {int} -- acknowledge #, a.k.a ack field
            
            Keyword Arguments:
                data {bytes} -- payload to send (default: {b'\x00'})
            """
            self.payload = data
            self.seq = sequence
            # self.aOrN = aN
            self.ack = acknowledge
            self.payload = data
            self.timesamp = None
            # status: True for live, False for dead
            self.status = True

        def construct(self) -> bytes:
            """construct(wrap) a packet: create the bytes to be sent through udp port
            
            Returns:
                bytes -- bytes to be transmit on udp
            """
            length = len(self.payload)
            # pack header info (except checksum)
            headerWOchecksum = struct.pack('HHH', self.seq, self.ack, length)
            # print("header: ", headerWOchecksum)
            packetWOchecksum = headerWOchecksum + self.payload
            # calculate checksum of the packet
            checksum = md5(packetWOchecksum)
            checksum = checksum.digest()
            frame = checksum + packetWOchecksum
            return frame

        @property
        def length(self) -> int:
            """the length of payload
            
            Returns:
                int -- length
            """
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
            result = Rudp.Packet.checksumL + Rudp.Packet.seqL + \
                Rudp.Packet.ackL + Rudp.Packet.lengthL
            return result

        @staticmethod
        def pack(sequence: int, acknowledge: int, data: bytes=b'\x00') -> bytes:
            """pack a packet in rudp way. requires seq # and ack#
            
            Arguments:
                sequence {int} -- seq#
                acknowledge {int} -- ack#
            
            Keyword Arguments:
                data {bytes} -- data to be sent (default: {b'\x00'})
            
            Returns:
                bytes -- wrapped frame
            """
            tempPacket = Rudp.Packet(sequence, acknowledge, data)
            return tempPacket.construct()

        @staticmethod
        def unpack(data: bytes) -> tuple:
            """unpack(parse) a rudp packet from udp data
            
            Arguments:
                data {bytes} -- data received through rudp
            
            Returns:
                tuple -- (Rudp.Packet, validity, client)
            """
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
