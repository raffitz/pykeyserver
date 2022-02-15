#!/usr/bin/env python3
"""HKP server

Uses the python http.server module to create an HKP keyserver (pykeyserver)

Functions:

    port(number or string or bytes or bytearray) -> 16 bit integer"""

import ipaddress
import argparse
import http.server
from http import HTTPStatus
import urllib.parse
import subprocess
import sys


KEYRING_PATH = './.server.gpg'


class HKPRequestHandler(http.server.BaseHTTPRequestHandler):
    """HKP Request Handler Class"""

    def hkp_index(self, search):
        """Handle the index and vindex request"""
        try:
            output = subprocess.run(['gpg', '--with-colons',
                                     '--no-default-keyring',
                                     '--keyring', KEYRING_PATH,
                                     '--list-keys',
                                     search],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    check=True)
            result = output.stdout
        except subprocess.CalledProcessError:
            result = ''
        keys = []
        count = 0
        for line in result.splitlines():
            if line.startswith('pub'):
                elements = line.split(':')
                # keyid = elements[4]
                # algo = elements[3]
                # keylen = elements[2]
                # creation_date = elements[5]
                # expiration_date = elements[6]
                # flags = elements[2]
                pub = f'pub:{elements[4]}:{elements[3]}:{elements[2]}:'
                pub += f'{elements[5]}:{elements[6]}:{elements[2]}'
                keys.append(pub)
                count += 1
            elif line.startswith('uid'):
                elements = line.split(':')
                uid_string = elements[9]
                uid = urllib.parse.quote(uid_string)
                # creation_date = elements[5]
                # expiration_date = elements[6]
                # flags = elements[2]
                uid = f'uid:{uid}:{elements[5]}:{elements[6]}:{elements[2]}'
                keys.append(uid)
        content = f'info:1:{count}\n'
        content += '\n'.join(keys)
        content += '\n'

        content = content.encode()

        content_lenth = len(content)
        self.send_response(HTTPStatus.OK)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Connection', 'close')
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', content_lenth)
        self.end_headers()
        self.wfile.write(content)

    def hkp_get(self, search):
        """Handle the HKP get request"""
        try:
            output = subprocess.run(['gpg', '--with-colons',
                                     '--no-default-keyring',
                                     '--keyring', KEYRING_PATH,
                                     '--list-keys',
                                     search],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    check=True)
            result = output.stdout
        except subprocess.CalledProcessError:
            result = ''
        keys = []
        count = 0
        for line in result.splitlines():
            if line.startswith('pub'):
                elements = line.split(':')
                keyid = elements[4]
                keys.append(keyid)
                count += 1
        try:
            command = ['gpg', '--with-colons', '--no-default-keyring',
                       '--keyring', KEYRING_PATH, '--armor',
                       '--export']
            command.extend(keys)
            output = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    encoding='utf-8',
                                    check=True)
            result = output.stdout
        except subprocess.CalledProcessError:
            result = ''
        content = result
        content = content.encode()
        content_lenth = len(content)
        self.send_response(HTTPStatus.OK)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Connection', 'close')
        self.send_header('Content-Type', 'application/pgp-keys')
        self.send_header('Content-Length', content_lenth)
        self.end_headers()
        self.wfile.write(content)

    def hkp_add(self):
        """Handle key adding"""
        if 'Content-Length' not in self.headers:
            self.send_error(HTTPStatus.LENGTH_REQUIRED)
            return
        value = self.headers['Content-Length']
        try:
            value = int(value)
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST)
            raise
        data = self.rfile.read(value).decode()
        decoded = urllib.parse.parse_qs(data)
        if 'keytext' not in decoded:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        armored = ''.join(decoded['keytext'])
        subprocess.run(['gpg', '--with-colons', '--no-default-keyring',
                        '--keyring', KEYRING_PATH, '--import'],
                       input=armored,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       encoding='utf-8',
                       check=False)
        self.send_response(HTTPStatus.OK)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Connection', 'close')
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', 0)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        path_parts = self.path.split('?', 1)
        hier_path = path_parts[0]
        if len(path_parts) == 2:
            args = urllib.parse.parse_qs(path_parts[1])
        else:
            args = {}
        if hier_path == '/pks/lookup':
            if 'op' in args and 'search' in args:
                cmd = args['op'][0]
                search = ' '.join(args['search'])
                if cmd in ['index', 'vindex']:
                    self.hkp_index(search)
                    return
                if cmd == 'get':
                    self.hkp_get(search)
                    return
                self.send_error(HTTPStatus.NOT_IMPLEMENTED)
                return
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        self.send_error(HTTPStatus.NOT_IMPLEMENTED)

    def do_POST(self):
        """Handle POST requests"""
        path_parts = self.path.split('?', 1)
        hier_path = path_parts[0]
        if hier_path == '/pks/add':
            self.hkp_add()
            return
        self.send_error(HTTPStatus.NOT_IMPLEMENTED)


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

    try:
        subprocess.run(['gpg', '--with-colons', '--no-default-keyring',
                        '--keyring', KEYRING_PATH, '--fingerprint'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print('Unable to create or open keyring')
        sys.exit(1)

    run_server(ip_address=args.address, tcp_port=args.port)


if __name__ == '__main__':
    main()
