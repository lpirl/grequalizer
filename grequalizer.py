#!python3 -OO
"""
This moduly mainly provides CLI interface.
"""

from sys import argv
from lib import ChecksRunner
from lib.util import log

def help_and_exit():
    log("script for maintaining an UNIX groups accounts and home directories")
    log("")
    log("usage: [python3] %s [config file]" % argv[0])
    log("  explicit call of 'python3' turns on debug")
    exit(0)

if __name__ == "__main__":
    if '--help' in argv or '-h' in argv:
        help_and_exit()

    try:
        runner = ChecksRunner(argv[1])
    except IndexError as exception:
        help_and_exit()
    runner.auto()
