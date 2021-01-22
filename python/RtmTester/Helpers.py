#!/usr/bin/env python3

def print_ok(msg, **kargs):
    """
    Print the message in green.
    """
    print(f"\033[32m{msg}\033[0m", **kargs)


def print_failed(msg, **kargs):
    """
    Print the message in red.
    """
    print(f"\033[31m{msg}\033[0m", **kargs)
