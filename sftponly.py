#!python3 -OO
"""
This moduly mainly provides CLI interface.
"""

from sys import argv
from lib import HomesChecker

if __name__ == "__main__":
    if '--help' in argv or '-h' in argv:
        log("script for maintaining users and ther chroots of a sftp-only server")
        log("")
        log("usage: [python3] ./sftponly.py [config file]")
        log("  explicit call with 'python3' turns on debug")
        log("  config file defaults to './sftponly.conf'")
        log("    see this file for an example configuration")
        exit(0)
    try:
        checker = HomesChecker(argv[1])
    except IndexError as exception:
        checker = HomesChecker()
    checker.auto()
