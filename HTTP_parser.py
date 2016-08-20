import re

http_request = "GET / HTTP/1.1\r\n" \
    "HOST: www.example.com\r\n" \
    "Accept: text/html, */*\r\n" \
    "Accept-Language: en-US\r\n" \
    "Accept-Encoding: gzip\r\n" \
    "Content-Length: 13\r\n" \
    "\r\n" \
    "tid=1&text=hi"

print(http_request)
request_component = http_request.split('\r\n')
request_component[0]  # status line

(method, path, http_version) = request_component[0].split(' ')
(method, path, http_version)

header = {k: v for k, v in [re.split(r'\s*:\s*', x, maxsplit=1) for x in request_component[1:-2]]}

for x in request_component[1:-2]:
    header_key, header_value = re.split(r'\s*:\s*', x, maxsplit=1)
    header[header_key] = header_value

header

body = request_component[-1]
body

(method, path, http_version, header, body)

