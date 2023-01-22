from enum import Enum


class Socket:
    class Protocol(Enum):
        TCP_IPV4 = '/proc/net/tcp'
        UDP_IPV4 = '/proc/net/udp'
        TCP_IPV6 = '/proc/net/tcp6'
        UDP_IPV6 = '/proc/net/udp6'

    class Status(Enum):
        TCP_ESTABLISHED = 1
        TCP_SYN_SENT = 2
        TCP_SYN_RECV = 3
        TCP_FIN_WAIT1 = 4
        TCP_FIN_WAIT2 = 5
        TCP_TIME_WAIT = 6
        TCP_CLOSE = 7
        TCP_CLOSE_WAIT = 8
        TCP_LAST_ACK = 9
        TCP_LISTEN = 10
        TCP_CLOSING = 11
        TCP_NEW_SYN_RECV = 12
        TCP_MAX_STATES = 13

    def __init__(self, proto, inode, local_addr, remote_addr, status, rx_queue, tx_queue):
        self.proto = proto
        self.inode = inode
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.status = Socket.Status(status)
        self.rx_queue = rx_queue
        self.tx_queue = tx_queue
