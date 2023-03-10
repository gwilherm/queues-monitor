import re
import time

from .proc import Proc
from .sock import Socket
from .csv_serializer import CsvSerializer


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
        self.running = True
        self.procs = []
        self.interval = args.interval
        self.csv = None

        if args.csv:
            self.csv = CsvSerializer(args.csv)

        for pid in args.pid_list:
            self.procs.append(Proc(pid))

    def stop(self, signum, frame):
        self.running = False

    def run(self):
        while self.running:
            now = time.time()
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
                            if self.csv:
                                self.csv.add_row(now, sock.inode, pr.pid, pr.name,
                                                 sock.local_addr, sock.remote_addr, sock.proto.name, sock.status.name,
                                                 sock.tx_queue, sock.rx_queue)
                else:
                    print(f'Proc[{pr.pid}] : not running.')

            time.sleep(self.interval)

        print('Terminating.')

        if self.csv:
            self.csv.close()
