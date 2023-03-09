FROM python:3.11.2-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /home
COPY . /home

RUN apt-get update && apt-get install -y libglib2.0-0 \
	build-essential \
	cmake \
	pkg-config \
	libavcodec-dev \
	libavformat-dev \
	libswscale-dev \
	libsm6 \
	libxext6 \ 
	libxrender-dev
	
RUN pip install -r requirements.txt
# COPY ./entrypoint.sh /home/docker-entrypoint.sh
RUN chmod +x /home/docker-entrypoint.sh
ENTRYPOINT ["/home/docker-entrypoint.sh"]

