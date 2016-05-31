#!/bin/sh

set -xe

# Check for required environment variables
if [ -z $INPUT_S3_BUCKET ]
then
    echo "INPUT_S3_BUCKET is not set"
    exit 1
fi

if [ -z $INPUT_S3_OBJECT_KEY ]
then
    echo "INPUT_S3_OBJECT_KEY is not set"
    exit 1
fi

mkdir -p /opt/builder/tmp
mkdir -p /opt/builder/workspace

aws s3 cp s3://$INPUT_S3_BUCKET/$INPUT_S3_OBJECT_KEY /opt/builder/tmp
unzip /opt/builder/tmp/$INPUT_S3_OBJECT_KEY -d /opt/builder/workspace

/opt/builder/workspace/build.sh
