#!/usr/bin/env python3
"""HKP server

Uses the python http.server module to create an HKP keyserver (pykeyserver)

Functions:

    port(number or string or bytes or bytearray) -> 16 bit integer"""

import ipaddress
import argparse
import http.server


class HKPRequestHandler(http.server.BaseHTTPRequestHandler):
    """HKP Request Handler Class"""


def run_server(server_class=http.server.ThreadingHTTPServer,
               handler_class=HKPRequestHandler,
               ip_address='',
               tcp_port=11371):
    """Run HTTP server with HKP request handler"""
    ip_address = str(ip_address)
    server_address = (ip_address, tcp_port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


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

    run_server(ip_address=args.address, tcp_port=args.port)


if __name__ == '__main__':
    main()
