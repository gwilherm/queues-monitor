import re
import time

from .proc import Proc
from .sock import Socket


def convert_linux_netaddr(address):
    hex_addr, hex_port = address.split(':')
    addr_list = re.findall('..', hex_addr)
    addr_list.reverse()
    addr = ".".join(map(lambda x: str(int(x, 16)), addr_list))
    port = str(int(hex_port, 16))
    return "{}:{}".format(addr, port)


def display(fd, sock):
    print(f' - Socket[{fd}] (Inode={sock.inode})')
    print(f'        `- {sock.local_addr} <=> {sock.remote_addr}')
    print(f'        `- Protocol\t= {sock.proto.name}')
    print(f'        `- Status\t= {sock.status.name}')
    print(f'        `- RX Queue\t= {sock.rx_queue}')
    print(f'        `- TX Queue\t= {sock.tx_queue}')


class Application:
    def __init__(self, args):
        self.procs = []
        self.interval = args.interval

        for pid in args.pid_list:
            self.procs.append(Proc(pid))

    def run(self):
        while True:
            print('\033c')
            net = dict()

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

            for pr in self.procs:
                pr.update(net)
                if pr.running:
                    print(f'Proc[{pr.pid}] : {pr.name}')
                    for fd in pr.sockets.keys():
                        sock = pr.sockets[fd]
                        if sock is not None:
                            display(fd, sock)
                else:
                    print(f'Proc[{pr.pid}] : not running.')

            time.sleep(self.interval)
