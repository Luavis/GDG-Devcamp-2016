import asyncio
import re


async def _handle(reader, writer):
    status_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]
    (method, path, http_version) = status_line.split(' ')

    headers = {}
    header_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]
    while len(header_line) > 0:
        header_key, header_value = re.split(r'\s*:\s*', header_line, maxsplit=1)
        headers[header_key] = header_value
        # read up next
        header_line = (await reader.readuntil(b'\r\n')).decode('ascii')[:-2]

    print((method, path, http_version, headers))
    response_data = """
        <html>
            <body>
                <h1>서버에여 파이썬 서버</h1>
            </body>
        </html>
    """
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Server: python/3.5.2\r\n"
        "Content-Length: {0}\r\n"
        "Content-Type: text/html; charset=\"utf-8\"\r\n"
        "Date: \r\n"
        "\r\n".format(len(response_data)))
        + response_data
    writer.write(response.encode('utf-8'))
    writer.close()


async def run_server(host="127.0.0.1", port=8888):
    print("Run server {0}:{1}".format(host, port))
    await asyncio.start_server(_handle, host, port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
    loop.run_forever()
