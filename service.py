from socket import *
import struct

def SendSvrd(host, port, info):
    ADDR = (host, port)

    # 创建一个socket
    tcpCliSock = socket(AF_INET, SOCK_STREAM)

    # 连接到服务端
    tcpCliSock.connect(ADDR)

    # struct.pack(fmt, v1, v2,...)
    buf = struct.pack(">cccccccci", b'H',b'R',b'P',b'C',bytes([1]),b'\0',b'\0',b'\0', len(info)) + info
    tcpCliSock.send(buf)
    tcpCliSock.close()