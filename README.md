# sweetmon2

Developement in still progress!

I will update readme for this project soon!

## What is this?

![2018-08-26 5 02 19](https://user-images.githubusercontent.com/14085555/44626103-fdc82e80-a951-11e8-98c7-8bd5f426c5b1.png)

Sweetmon2 is a fuzzer monitoring framework based Python3 + Django2. User can check their fuzzers and crashes on the web. It can reduce repetitive work for fuzz testers.

## Screenshots

### Fuzzer configuration

![2018-08-26 5 05 11](https://user-images.githubusercontent.com/14085555/44626127-69120080-a952-11e8-854b-78ac7a44fd5a.png)



### Fuzzer list

![2018-08-26 5 05 26](https://user-images.githubusercontent.com/14085555/44626128-69aa9700-a952-11e8-8a9c-49f5903a3317.png)



### Crash list

![2018-08-26 5 09 02](https://user-images.githubusercontent.com/14085555/44626172-f81f1880-a952-11e8-9043-6c17abaca62b.png)



### Crash detail

![2018-08-26 5 09 33](https://user-images.githubusercontent.com/14085555/44626170-f35a6480-a952-11e8-9acc-46f154eeb63d.png)



### Duplicate crashes

![2018-08-26 5 09 41](https://user-images.githubusercontent.com/14085555/44626182-200e7c00-a953-11e8-80b0-df662d9ed205.png)



### Storage list

![2018-08-26 5 06 12](https://user-images.githubusercontent.com/14085555/44626171-f6edeb80-a952-11e8-8aaa-09d4b4835be7.png)



### Storage Details

![2018-08-26 5 12 08](https://user-images.githubusercontent.com/14085555/44626188-39172d00-a953-11e8-9566-678ded58ddb6.png)



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