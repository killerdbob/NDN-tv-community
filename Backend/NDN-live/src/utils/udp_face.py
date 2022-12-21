from asyncio.transports import Transport
from ndn.transport.stream_socket import StreamFace, TcpFace as NdnTcpFace
from socket import AF_INET, AF_INET6, SOCK_DGRAM, socket
from ndn.client_conf import read_client_conf, default_face as ndn_default_face
from config import TCP_BUFFER_SIZE
import logging

import asyncio as aio


class UdpFace(StreamFace):

    def __init__(self, host='localhost', port=6363, ip_version=AF_INET):
        super().__init__()
        self.__host = host
        self.__port = port
        self.__ip_version = ip_version

    async def open(self):
        sock = socket(self.__ip_version, SOCK_DGRAM)
        sock.connect((self.__host, self.__port))
        self.reader, self.writer = await aio.open_connection(sock=sock)
        self.running = True


class TcpFace(NdnTcpFace):

    async def open(self):
        self.reader, self.writer = await aio.open_connection(self.host, self.port, limit=TCP_BUFFER_SIZE)
        self.running = True


def default_face():
    config = read_client_conf()
    transport = config['transport']
    if transport.startswith('udp'):
        hostBegin = len('udp')
        if transport[hostBegin] == '4':
            ip_version = AF_INET
            hostBegin += 1
        elif transport[hostBegin] == ':':
            ip_version = AF_INET
        else:
            ip_version = AF_INET6
            hostBegin += 1
        hostBegin += len('://')
        hostEnd = transport.find(':', hostBegin)
        if hostEnd >= 0:
            port = int(transport[hostEnd + 1:])
        else:
            port = 6363
        host = transport[hostBegin:] if hostEnd < 0 else transport[hostBegin: hostEnd]
        return UdpFace(host, port, ip_version)
    elif transport.startswith('tcp'):
        hostBegin = len('tcp')
        if transport[hostBegin] != ':':
            hostBegin += 1
        hostBegin += len('://')
        hostEnd = transport.find(':', hostBegin)
        port = 6363 if hostEnd < 0 else int(transport[hostEnd + 1:])
        host = transport[hostBegin:] if hostEnd < 0 else transport[hostBegin: hostEnd]
        return TcpFace(host, port)
    else:
        return ndn_default_face(transport)
