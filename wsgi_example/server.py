import asyncio
import re
import sys

APPLICATION = None
SERVER_PORT = 8888


def wsgi_to_bytes(s):
    return s.encode('iso-8859-1')


async def _handle(reader, writer):
    status_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]
    (method, path, http_version) = status_line.split(' ')

    headers = {}
    header_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]
    while len(header_line) > 0:
        header_key, header_value = re.split(r'\s*:\s*', header_line, maxsplit=1)
        headers[header_key.upper()] = header_value
        # read up next
        header_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]

    print('[{0}] - {1}'.format(method, path))
    if '?' in path:
        (path, query) = path.split('?')
    else:
        query = ''

    # WSGI work!

    environ = {'HTTP_{0}'.format(k.replace('-', '_')): v for k, v in headers.items()}
    environ['wsgi.input'] = writer
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = True
    environ['wsgi.multiprocess'] = False
    environ['wsgi.url_scheme'] = 'http'
    environ['SERVER_NAME'] = 'Python/3.5.2'
    environ['SERVER_PORT'] = SERVER_PORT
    environ['REQUEST_METHOD'] = method
    environ['PATH_INFO'] = path
    environ['QUERY_STRING'] = query
    environ['CONTENT_TYPE'] = headers.get('CONTENT-TYPE') or ''
    environ['CONTENT_LENGTH'] = int(headers.get('CONTENT_LENGTH') or 0)
    environ['SERVER_PROTOCOL'] = http_version

    headers_set = []
    headers_sent = []

    def write(data):
        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            status, response_headers = headers_sent[:] = headers_set
            writer.write(wsgi_to_bytes('HTTP/1.1 %s' % status))
            for header in response_headers:
                writer.write(wsgi_to_bytes('%s: %s\r\n' % header))
            writer.write(wsgi_to_bytes('\r\n'))

        writer.write(data)

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]

        return write

    result = APPLICATION(environ, start_response)

    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()
        writer.close()


async def run_server(host="127.0.0.1", port=8888):
    global SERVER_PORT
    SERVER_PORT = str(port)
    print("Run server {0}:{1}".format(host, port))
    await asyncio.start_server(_handle, host, port)


def start_server(_app):
    global APPLICATION
    APPLICATION = _app
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
    loop.run_forever()
