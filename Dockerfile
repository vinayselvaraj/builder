FROM alpine
MAINTAINER Vinay Selvaraj <vinay@selvaraj.com>

RUN apk add --update    \
            python      \
            py-pip      \
            make

RUN pip2.7 install --upgrade pip
RUN pip2.7 install awscli

RUN mkdir -p /opt/builder/bin
COPY ./builder.sh /opt/builder/bin

ENTRYPOINT /opt/builder/bin/builder.sh
