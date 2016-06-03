FROM centos:7
MAINTAINER Vinay Selvaraj <vinay@selvaraj.com>

RUN yum -y install python docker

# Install PIP
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "/tmp/get-pip.py"
RUN python2.7 /tmp/get-pip.py
RUN pip2.7 install --upgrade pip

# Install AWS CLI
RUN pip2.7 install awscli

RUN mkdir -p /opt/builder/bin
COPY ./builder.sh /opt/builder/bin

ENTRYPOINT /opt/builder/bin/builder.py
