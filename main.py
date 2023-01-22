#!/bin/env python3

import sys
from internal import Application


def main(argv):
    Application(argv).run()


if __name__ == '__main__':
    main(sys.argv[1:])
