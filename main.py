#!/bin/env python3

import sys
import argparse
from internal import Application


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('pid_list', metavar='PID', type=int, nargs='+',
                        help='List of PIDs to monitor')
    parser.add_argument('-n', '--interval', help="Refresh interval in seconds", type=float, required=False, default=1)

    args = parser.parse_args()

    print(args)

    Application(args).run()


if __name__ == '__main__':
    main(sys.argv[1:])
