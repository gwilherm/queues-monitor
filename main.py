#!/bin/env python3

import sys
import signal
import argparse
from internal import Application


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('pid_list', metavar='PID', type=int, nargs='+',
                        help='List of PIDs to monitor')
    parser.add_argument('-n', '--interval', help="Refresh interval in seconds", type=float, required=False, default=1)
    parser.add_argument('-c', '--csv', help="Serialize to CSV file", required=False)

    args = parser.parse_args()

    app = Application(args)

    signal.signal(signal.SIGINT, app.stop)

    app.run()


if __name__ == '__main__':
    main(sys.argv[1:])
