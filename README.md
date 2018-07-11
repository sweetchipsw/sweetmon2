# sweetmon2

Developement in progress!

I will update readme for this project soon!

## Installation

Sweetmon2 supports docker to make easy installing this project.

```bash
docker build --no-cache=true --tag sweetmon2 . #
```



```sh
root@ubuntu:~/sweetmon# docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
sweetmon2           latest              1824b348c743        21 hours ago        635 MB
```



```sh
docker run -p 80:80 -d -it 1824b348c743 /bin/bash -c 'apachectl -D FOREGROUND'
```



```Sh
curl http://localhost/accounts/login
```



## API Documentation

SEE [Here](https://github.com/sweetchipsw/sweetmon2/blob/master/API_DOCS.md)
