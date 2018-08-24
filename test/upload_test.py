import requests
import socket
import random
import time
import json

# Define common headers
ENDPOINT_URL = "http://172.16.101.130/api/v1"
header = {"apikey":"5d69b264e8ec7aa05fd08b708545c2ed3d51ab6237f30df3f91a7ad7cdc336a3"}

print("[*] SIMPLE TEST")
random.seed(time.time())

##############################################################################
# CRASH UPLOAD TEST
i = random.randint(0, 0xfffff)
post = {"title":"""==="""+str(i)+"""===ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""",
"crashlog":"test\ntest"}
files = {'file': "NEW FILE TEST"}
r = requests.post(ENDPOINT_URL+"/crash/upload", files=files, data=post, headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] Upload : PASS")
else:
    print("[*] Upload : FAIL")
##############################################################################

##############################################################################
# DUPLICATED CRASH UPLOAD TEST
post = {"title":"""==="""+str(i)+"""===ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""",
"crashlog":"test\ntest"}
files = {'file': "NEW FILE TEST"}
r = requests.post(ENDPOINT_URL+"/crash/upload", files=files, data=post, headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] DUP Upload : PASS")
else:
    print("[*] DUP Upload : FAIL")
##############################################################################

##############################################################################
# Ping
r = requests.get(ENDPOINT_URL+"/fuzzer/ping", headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] PING : PASS")
else:
    print("[*] PING : FAIL")
##############################################################################

##############################################################################
# Update fuzzer's IP informations.
public_ip = requests.get("http://ipv4bot.whatismyipaddress.com").text
private_ip = socket.gethostbyname(socket.gethostname())

post = {"public_ip" : public_ip, "private_ip" : private_ip}
r = requests.post(ENDPOINT_URL+"/fuzzer/update_info", post, headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] IP UPDATE : PASS")
else:
    print("[*] IP UPDATE : FAIL")
##############################################################################

##############################################################################
# Get storage list
r = requests.get(ENDPOINT_URL+"/storage/list", headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] STORAGE LIST : PASS")
else:
    print("[*] STORAGE LIST : FAIL")
##############################################################################
