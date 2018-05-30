import requests

header = {"apikey":"6faeee3fccba970636b11c7c920e0a151d32824bc9e6a9ff3ff6d4a62343e1fd"}

post = {"title":"""==9901==ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""", "crashlog":"test\ntest"}
files = {'file': "TEST FILE\nTEST FILE"}

r = requests.post("http://localhost:8000/api/v1/crash/upload", files=files, data=post, headers=header)
print(r.text)


r = requests.get("http://localhost:8000/api/v1/fuzzer/ping", headers=header)
print(r.text)

r = requests.get("http://localhost:8000/api/v1/storage/list", headers=header)
print(r.text)

