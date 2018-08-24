FROM ubuntu:16.04
MAINTAINER sweetchip <sweetchip@sweetchip.kr>

ENV LOCATION=/app
ARG MYSQL_DATABASE
ARG MYSQL_USER
ARG MYSQL_PASSWORD
ARG LANG
ARG LC_ALL
ENV MYSQL_DATABASE $MYSQL_DATABASE
ENV MYSQL_USER $MYSQL_USER
ENV MYSQL_PASSWORD $MYSQL_PASSWORD
ENV LANG $LANG
ENV LC_ALL $LC_ALL

# Update system
RUN apt update
#RUN apt upgrade -y
RUN apt install -y python3 python3-pip apache2 virtualenv libapache2-mod-wsgi-py3 git python3-pymysql
RUN apt install -y gettext-base
# Make working directory and go to /app
RUN mkdir -p /app
WORKDIR /app

# Download sweetmon from git repository
RUN git clone https://github.com/sweetchipsw/sweetmon2.git

# Set virtual environment
#RUN virtualenv -p python3 $VENV
#ENV PIP3=$LOCATION/$VENV/bin/pip3
#ENV PYTHON3=$LOCATION/$VENV/bin/python3

# Copy files into Docker.
ADD ./ /app
RUN envsubst < sweetmon.conf > /tmp/sweetmon.conf
RUN cp /tmp/sweetmon.conf /etc/apache2/sites-available/sweetmon2.conf
RUN a2dissite 000-default

# Setting Apache2
RUN a2ensite sweetmon2
RUN service apache2 restart

# Cleaning
RUN rm /tmp/sweetmon.conf

# Initialize sweetmon
WORKDIR /app/sweetmon2
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

# Create upload directories
RUN mkdir -p /data/file/crash/
RUN mkdir -p /data/file/users/
RUN mkdir -p /data/file/image/

EXPOSE 80
EXPOSE 443

# Set Permission
WORKDIR /app
RUN echo "[*] Initialize file permissions."
RUN chown www-data:www-data ./ -R

CMD ["apachectl", "-D", "FOREGROUND"]