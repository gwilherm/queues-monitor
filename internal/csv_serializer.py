import csv


class CsvSerializer:
    headers = ['time', 'inode', 'pid']

    def __init__(self, filename):
        self.fd = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.fd)
        self.csv_writer.writerow(['time', 'inode', 'pid',
                                  'local_addr', 'remote_addr', 'proto',
                                  'status', 'tx_queue', 'rx_queue'])
        self.fd.flush()

    def add_row(self, time, inode, pid, local_addr, remote_addr, proto, status, tx_queue, rx_queue):
        self.csv_writer.writerow([time, inode, pid, local_addr, remote_addr, proto, status, tx_queue, rx_queue])

    def close(self):
        self.fd.close()
