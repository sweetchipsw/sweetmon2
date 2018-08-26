# sweetmon2

Developement in still progress!

I will update readme for this project soon!

## What is this?

Sweetmon2 is a fuzzer monitoring framework based Python3 + Django2. User can check their fuzzers and crashes on the web. It can reduce repetitive work for fuzz testers.

## Notice

### Use at your own risk

THIS IS NOT STABLE VERSION! USE AT YOUR OWN RISK.

## Prepare

First of all, Please clone this project into your server.

```git clone https://github.com/sweetchipsw/sweetmon2.git```

Sweetmon2 supports docker to make install this project easier. It creates docker container that contains Web and Database on your server automatically. But, some of sensitive information(secret key, default ID and password) are included in installer which needs to access DB server or create server. So you must CHANGE these before you run the installer.

```
# List of sensitive informations

```



## Installation

### Dependencies

You should install some of dependencies to create sweetmon2 container by docker.

```bash
# Download docker
sudo apt install docker.io

# Download docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose

# Make it to executable
sudo chmod +x /usr/local/bin/docker-compose
```

### Create sweetmon2 container 

After you install the dependencies, move your working directory to ```/sweetmon2/install/``` and type under commands.

```bash
# Create docker container by using docker-compose
sudo docker-compose up -d

# Make ./data/ directory to persistent sweetmon2 data (crashes, files, etc)
sudo mkdir -p ./data/file/crash
sudo mkdir -p ./data/file/users

# 
sudo chmod 777 ./data/ -R
```

When the docker-compose job completed, you will see two containers

```bash
# Check container ID of 'sweetmon2-web' container.
sweetchip@ubuntu:~/sweetmon2/install$ sudo docker ps
CONTAINER ID        IMAGE                   COMMAND                  CREATED              STATUS              PORTS                         NAMES
4b372faec196        install_sweetmon2-web   "apachectl -D FORE..."   About a minute ago   Up About a minute   0.0.0.0:80->80/tcp, 443/tcp   sweetmon2-web
75373984ae0f        mariadb:latest          "docker-entrypoint..."   About a minute ago   Up About a minute   3306/tcp                      sweetmon2-db

# 4b372faec196 is sweetmon2-web's container ID.
# 4b372faec196        install_sweetmon2-web   "apachectl -D FORE..."   About a minute ago   Up About a minute   0.0.0.0:80->80/tcp, 443/tcp   sweetmon2-web

# Create database scheme
# Replace [CONTAINER ID] to your 'CONTAINER ID'. (In this example, 4b372faec196 is valid value.)
sudo docker exec -it [CONTAINER ID] python3 /app/sweetmon2/manage.py makemigrations

# Apply DB scheme on maria server
sudo docker exec -it [CONTAINER ID] python3 /app/sweetmon2/manage.py migrate

# Create new user (Super user)
sudo docker exec -it [CONTAINER ID] python3 /app/sweetmon2/manage.py createsuperuser
```

All done!

Open your web browser, and go to ```http://SERVER-IP-ADDRESS/```.

## Example

### Upload crash on server

```python
import requests
import socket
import random
import time
import json

# Define common headers
ENDPOINT_URL = "http://SWEETMON2-DOMAIN/api/v1"

# API KEY from sweetmon2
header = {"apikey":"a44087ec8cf60d7a9962babfde55be8284d1a966e4cb53c8b60978f427ae7c85"}

# CRASH UPLOAD TEST
post = {"title":"""===31337===ERROR: AddressSanitizer: heap-use-after-free on address 0x60700000dfb5 at pc 0x45917b bp 0x7fff4490c700 sp 0x7fff4490c6f8 READ of size 1 at 0x60700000dfb5 thread T0""",
"crashlog":"CRASH LOG CONTENTS"}
files = {'file': "CRASH FILE CONTENTS"}
r = requests.post(ENDPOINT_URL+"/crash/upload", files=files, data=post, headers=header)
result = json.loads(r.text)
if result['result']:
    print("[*] Upload : Success")
else:
    print("[*] Upload : Fail")
```

For more API informations, Check this [API Documentations](https://github.com/sweetchipsw/sweetmon2/blob/master/API_DOCS.md).

## API

Sweetmon2 supports APIs to interact with your fuzzer.

To get more informations, check this [API Documentations](https://github.com/sweetchipsw/sweetmon2/blob/master/API_DOCS.md).