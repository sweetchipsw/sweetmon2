FROM ubuntu:16.04
MAINTAINER sweetchip <sweetchip@sweetchip.kr>

#volume ["/data/"]

#ENV VENV=sweetmon_venv
ENV LOCATION=/app
#ENV ADMIN_ID=admin
#ENV ADMIN_PW=adm1npasswd

# Update system
RUN apt update
#RUN apt upgrade -y
RUN apt install -y python3 python3-pip apache2 virtualenv libapache2-mod-wsgi-py3 git
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

# Create Superuser (CHANGE PASSWORD IMMEDIATELY AFTER INSTALL FINISHED)
#RUN $PYTHON3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$ADMIN_ID', 'admin@example.com', '$ADMIN_PW')"

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
