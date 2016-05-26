FROM alpine
MAINTAINER Vinay Selvaraj <vinay@selvaraj.com>

RUN apk add --update    \
            python      \
            py-pip      \
            make

RUN pip2.7 install --upgrade pip
RUN pip2.7 install boto3

RUN mkdir -p /opt/builder
COPY ./builder.py /opt/builder

ENTRYPOINT /usr/bin/python2.7 /opt/builder/builder.py
