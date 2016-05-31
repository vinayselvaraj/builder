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

if [ -z $DOCKER_IMAGE_NAME ]
then
    echo "DOCKER_IMAGE_NAME is not set"
    exit 1
fi

if [ -z $DOCKER_IMAGE_TAG ]
then
    echo "DOCKER_IMAGE_TAG is not set"
    exit 1
fi

BUILDER_HOME=/opt/builder
WORKSPACE=$BUILDER_HOME/workspace

mkdir -p $BUILDER_HOME/tmp
mkdir -p $WORKSPACE

aws s3 cp s3://$INPUT_S3_BUCKET/$INPUT_S3_OBJECT_KEY $BUILDER_HOME/tmp
unzip $BUILDER_HOME/tmp/$INPUT_S3_OBJECT_KEY -d $WORKSPACE

cd $WORKSPACE

if [ -e $WORKSPACE/build.sh ]
then
    /opt/builder/workspace/build.sh
fi

if [ ! -e $WORKSPACE/Dockerfile ]
then
    echo "Unable to find Dockerfile"
    exit 1
fi

docker build -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG .

