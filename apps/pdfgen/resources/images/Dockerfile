# Dockerfile for tasks requiring LuxRender.

FROM golemfactory/base:1.2

MAINTAINER Artur Zawłocki <artur.zawlocki@imapp.pl>

ENV PDFGEN_DIR=/home/task/PDFGEN

RUN mkdir /golem/pdfgen && \
    apt-get update && \
	apt-get install -y \
        apt-utils \
		curl \
		bzip2 \
        git \
        libjpeg-dev zlib1g-dev\
        python-dev \
        python-pip\
        libtool \
        automake \
        make \
		libglu1-mesa \
		libgomp1 && \
    apt-get upgrade -y &&\
	apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/* &&\
    pip install reportlab pypdf2
