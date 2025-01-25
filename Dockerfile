# -----------------------------
# KISB Core Dockerfile
# Environment: Python3
# Minimum Panel Version: 0.6.0
# -----------------------------

FROM python:3.11-alpine

LABEL maintainer="J Stuff"
LABEL email="jstuff@j-stuff.net"

# Make KISB
RUN mkdir /KISB




# Lets KISB know its running in a docker environment. Mainly used to change datastore location
ENV IS_DOCKER=true 

# Force KISB to use the NZ timezone
ENV TZ=Pacific/Auckland



COPY ./src /KISB
COPY ./requirements.txt /KISB/requirements.txt


RUN pip install --no-cache-dir -q -r /KISB/requirements.txt

# RUN mkdir /home/container/cache
# RUN mkdir /home/container/data
# RUN mkdir /home/container/data/discord

# RUN touch /home/container/data/discord/discord.json

# Pterodactyl requirements
RUN adduser --disabled-password --home /home/container container

USER container
ENV  USER=container HOME=/home/container

WORKDIR /home/container


CMD ["python", "/KISB/main.py"]