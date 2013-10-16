"""
Module for everything that does not fit into one of the other modules.
"""

from inspect import stack

COLOR_STD = '\033[0m'
COLOR_FAIL = '\033[31m'
COLOR_LIGHT = '\033[33m'

def debug(msg):
    """
    helper method to honor __debug__ for debug printing
    """
    if __debug__:
        depth = len(stack()) - 3
        print(' '*depth, msg)

def log(msg):
    """
    Since this script is used in cron and cron sends mails if there is
    stdout, we print ordinarily.
    """
    print(msg)
