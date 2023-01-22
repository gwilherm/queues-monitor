#!/bin/env python3

import sys
import os
import re
import time
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


class Proc:
    def __init__(self, pid):
        self.pid = pid
        self.running = True
        self.proc_path = f'/proc/{self.pid}'
        self.name = self.get_proc_name()
        self.sockets = dict()

    def get_proc_name(self):
        name = None
        status_file = os.path.join(self.proc_path, 'comm')
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    name = f.readline().strip()
            except IOError:
                name = None

        return name

    def update(self, net):
        if os.path.exists(self.proc_path):
            fd_path = os.path.join(self.proc_path, 'fd')
            for file in os.listdir(fd_path):
                file = os.path.join(fd_path, file)
                fd = os.path.basename(file)
                tg = os.path.basename(os.path.realpath(file))
                if tg.startswith('socket:'):
                    inode = re.match('socket:\\[(\\d+)]', tg).group(1)
                    self.sockets[fd] = net.get(inode)
        else:
            self.running = False


def convert_linux_netaddr(address):
    hex_addr, hex_port = address.split(':')
    addr_list = re.findall('..', hex_addr)
    addr_list.reverse()
    addr = ".".join(map(lambda x: str(int(x, 16)), addr_list))
    port = str(int(hex_port, 16))
    return "{}:{}".format(addr, port)


def main(argv):
    procs = []

    for pid in argv:
        procs.append(Proc(pid))

    while True:
        print('\033c')
        net = dict()
        sockets = []

        for proto in Socket.Protocol:
            with open(proto.value) as f:
                for line in f.readlines()[1:]:
                    cols = re.split(r'\s+', line.strip())
                    local_addr = convert_linux_netaddr(cols[1])
                    remote_addr = convert_linux_netaddr(cols[2])
                    status = int(cols[3], 16)
                    tx, rx = [int(cpt, 16) for cpt in cols[4].split(':')]
                    inode = cols[9]
                    try:
                        net[inode] = Socket(proto, inode, local_addr, remote_addr, status, rx, tx)
                    except KeyError:
                        net[inode] = None

        for pr in procs:
            pr.update(net)
            print(f'Proc[{pr.pid}] : {pr.name}')
            for fd in pr.sockets.keys():
                sock = pr.sockets[fd]
                if sock is not None:
                    print(f' - Socket[{fd}] (Inode={sock.inode})')
                    print(f'        `- {sock.local_addr} <=> {sock.remote_addr}')
                    print(f'        `- Protocol\t= {sock.proto.name}')
                    print(f'        `- Status\t= {sock.status.name}')
                    print(f'        `- RX Queue\t= {sock.rx_queue}')
                    print(f'        `- TX Queue\t= {sock.tx_queue}')

        time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1:])
