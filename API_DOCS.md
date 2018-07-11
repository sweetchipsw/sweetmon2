# API Documenation for Sweetmon2

This documenation provides API informations of `Sweetmon2`. To use `Sweetmon2`, You should interact with your fuzzer and `Sweetmon2`. All of example codes are written in Python3. Please install requests module to use under examples codes.

### API Endpoint

- https://YOURSERVERDOMAIN/api/v1/

## Notice

You should send data to server with **API KEY** in HTTP headers.

## URL routers in sweetmon2

There are three external APIs to get fuzzing data from your fuzzer client. and you can find this information at `/api/urls.py`.

```python
# /api/urls.py
# APIs for interacting with clients.
path('crash/upload', views.crash_upload, name='crash-upload-crash'),
path('fuzzer/update_info', views.fuzzer_update_info, name='fuzzer-update-client'),
path('fuzzer/ping', views.fuzzer_ping, name='fuzzer-ping'),
```

## APIS

### Upload crashes

URL : ```/crash/upload```

Method : ```POST```

Parameter 

| Field    | Type   | Description       |
| -------- | ------ | ----------------- |
| title    | string | Tile of crash     |
| crashlog | string | Log file of crash |
| file     | binary | Contents of crash |

Example

```python
import requests 

# Define common headers
ENDPOINT_URL = "http://localhost:8000/api/v1"
header = {"apikey":"6faeee3fccba970636b11c7c920e0a151d32824bc9e6a9ff3ff6d4a62343e1fd"}

# Upload test
post = {"title":"""==9901==ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""", "crashlog":"test\ntest"}
files = {'file': "TEST FILE\nTEST FILE IS TEST"}
r = requests.post(ENDPOINT_URL+"/crash/upload", files=files, data=post, headers=header)
print(r.text)
```

Response

```json
// If success,
{"result": true, "message": null}
```

### Ping

To let server know that client is alive,

URL : ```/fuzzer/ping```

Method : ```GET```

Parameter : None

Example

```python
import requests 

# Define common headers
ENDPOINT_URL = "http://localhost:8000/api/v1"
header = {"apikey":"6faeee3fccba970636b11c7c920e0a151d32824bc9e6a9ff3ff6d4a62343e1fd"}

# Ping
r = requests.get(ENDPOINT_URL+"/fuzzer/ping", headers=header)
print(r.text)

```

Response

```json
// If success,
{"result": true, "message": null}
```

### Update fuzzer's IP information

blah

URL : ```/fuzzer/update_info```

Method : ```POST```

Parameter : None

| Field      | Type   | Description                 |
| ---------- | ------ | --------------------------- |
| public_ip  | string | Client's public IP address  |
| private_ip | string | Client's private IP address |

해당 API 는 파라미터가 필요 없습니다.

Example

```python
import requests 
import socket

# Define common headers
ENDPOINT_URL = "http://localhost:8000/api/v1"
header = {"apikey":"6faeee3fccba970636b11c7c920e0a151d32824bc9e6a9ff3ff6d4a62343e1fd"}

# Get public IP address from 'whatismyipaddress.com'
public_ip = requests.get("http://ipv4bot.whatismyipaddress.com").text
# Get private IP address by using socket module
private_ip = socket.gethostbyname(socket.gethostname())

post = {"public_ip" : public_ip, "private_ip" : private_ip}
r = requests.post(ENDPOINT_URL+"/fuzzer/update_info", post, headers=header)
print(r.text)
```

Response

```json
// If success,
{"result": true, "message": null}
```

