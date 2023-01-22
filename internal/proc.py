import os
import re


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
