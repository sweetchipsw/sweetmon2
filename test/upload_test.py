import requests
import socket

"""
    # One time url
    path('share/download', views.file_download_by_otu, name='Download-file-by-OTU'),

    # Internal API
    path('crash/<int:idx>/download', views.crash_download, name='crash-download-directly'),
    path('crash/<int:idx>/generate_url', views.crash_generate_url, name='crash-generate-OTU'),
    path('crash/<int:idx>/duplicated_list', views.crash_dup_crash_list, name='crash-duplicated-crash'),

    # APIs for interacting with clients.
    path('crash/upload', views.crash_upload, name='crash-upload-crash'),
    path('fuzzer/update_info', views.fuzzer_update_info, name='fuzzer-update-client'),
    path('fuzzer/ping', views.fuzzer_ping, name='fuzzer-ping'),

    path('storage/list', views.storage_list, name='storage-list'),
    path('storage/download', views.storage_download, name='storage-download'),  # API
    path('storage/<int:idx>/download', views.storage_download_web, name='storage-download-on-web'),  # Web
    path('storage/<int:idx>/generate_url', views.storage_generate_url, name='storage-generate-OTU'),  # Web
"""

"""

TEST APIS

"""

# Define common headers
ENDPOINT_URL = "http://localhost:8000/api/v1"
header = {"apikey":"6faeee3fccba970636b11c7c920e0a151d32824bc9e6a9ff3ff6d4a62343e1fd"}

# Upload test
post = {"title":"""==9901==ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""", "crashlog":"test\ntest"}
files = {'file': "TEST FILE\nTEST FILE IS TEST"}
r = requests.post(ENDPOINT_URL+"/crash/upload", files=files, data=post, headers=header)
print(r.text)

# Ping
r = requests.get(ENDPOINT_URL+"/fuzzer/ping", headers=header)
print(r.text)

# Update fuzzer's IP informations.

public_ip = requests.get("http://ipv4bot.whatismyipaddress.com").text
private_ip = socket.gethostbyname(socket.gethostname())

post = {"public_ip" : public_ip, "private_ip" : private_ip}
r = requests.post(ENDPOINT_URL+"/fuzzer/update_info", post, headers=header)
print(r.text)

# Get storage list
r = requests.get(ENDPOINT_URL+"/storage/list", headers=header)
print(r.text)



"""

TEST WEB API

"""

