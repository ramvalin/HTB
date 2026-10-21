
#!/usr/bin/env python3
import socket
import struct
import sys

SOCKET_PATH = "/run/php-fpm/php-gromox-fpm.sock"
SCRIPT_PATH = "/root/mapi_diag.php"
REQUEST_ID = 1

FCGI_BEGIN_REQUEST = 1
FCGI_END_REQUEST = 3
FCGI_PARAMS = 4
FCGI_STDIN = 5
FCGI_STDOUT = 6
FCGI_STDERR = 7


def record(kind, content=b""):
    padding = (-len(content)) % 8
    header = struct.pack(
        "!BBHHBB", 1, kind, REQUEST_ID,
        len(content), padding, 0
    )
    return header + content + b"\0" * padding


def encode_length(length):
    if length < 128:
        return bytes([length])
    return struct.pack("!I", length | 0x80000000)


def encode_params(params):
    result = bytearray()
    for name, value in params.items():
        name = name.encode()
        value = value.encode()
        result += encode_length(len(name))
        result += encode_length(len(value))
        result += name + value
    return bytes(result)


def read_exact(sock, count):
    chunks = bytearray()
    while len(chunks) < count:
        part = sock.recv(count - len(chunks))
        if not part:
            break
        chunks.extend(part)
    return bytes(chunks)


def main():
    params = {
        "GATEWAY_INTERFACE": "CGI/1.1",
        "REQUEST_METHOD": "GET",
        "SCRIPT_FILENAME": SCRIPT_PATH,
        "SCRIPT_NAME": "/mapi_diag.php",
        "DOCUMENT_ROOT": "/",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "80",
        "REMOTE_ADDR": "127.0.0.1",
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
    }

    begin = struct.pack("!HB5s", 1, 0, b"\0" * 5)

    request = (
        record(FCGI_BEGIN_REQUEST, begin)
        + record(FCGI_PARAMS, encode_params(params))
        + record(FCGI_PARAMS)
        + record(FCGI_STDIN)
    )

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect(SOCKET_PATH)
        sock.sendall(request)

        while True:
            header = read_exact(sock, 8)
            if len(header) != 8:
                break

            _, kind, _, length, padding, _ = struct.unpack(
                "!BBHHBB", header
            )

            content = read_exact(sock, length)
            if len(content) != length:
                raise RuntimeError("Incomplete FastCGI response")

            if padding:
                read_exact(sock, padding)

            if kind in (FCGI_STDOUT, FCGI_STDERR):
                sys.stdout.write(content.decode(errors="replace"))

            if kind == FCGI_END_REQUEST:
                break


if __name__ == "__main__":
    main()

