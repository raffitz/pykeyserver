#!/usr/bin/env python3
"""HKP server

Uses the python http.server module to create an HKP keyserver (pykeyserver)

Functions:

    port(number or string or bytes or bytearray) -> 16 bit integer"""

import ipaddress
import argparse


def port(val):
    """Restrict port values to the TCP range.

    Receives a number or a string, bytes, or bytearray instance representing an
    integer literal.
    Raises ValueError if it's not a number or if the number falls outside TCP
    port range."""
    num = int(val)
    if num < 1:
        raise ValueError
    if num.bit_length() > 16:
        raise ValueError
    return num


def main():
    """HKP server main function"""
    parser = argparse.ArgumentParser(description='Basic HKP keyserver')
    parser.add_argument('--address',
                        type=ipaddress.ip_address,
                        help='IP for server interface',
                        default=ipaddress.ip_address('127.0.0.1'))
    parser.add_argument('--port',
                        type=port,
                        help='TCP Port for server interface',
                        default=port(11371))

    args = parser.parse_args()

    print(f'Server address parsed as {args.address}, port as {args.port}')


if __name__ == '__main__':
    main()
