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



# Install dependencies
yum -y install unzip

BUILDER_HOME=/opt/builder
WORKSPACE=$BUILDER_HOME/workspace

mkdir -p $BUILDER_HOME/tmp
mkdir -p $WORKSPACE

# Enable SigV4
aws configure set s3.signature_version s3v4
aws s3 cp s3://$INPUT_S3_BUCKET/$INPUT_S3_OBJECT_KEY $BUILDER_HOME/tmp/source.zip

# Set image name
IMAGE_NAME=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG

# Send image name to build output location
TMPFILE=`mktemp`
echo $IMAGE_NAME > $TMPFILE
aws s3 cp $TMPFILE s3://$OUTPUT_S3_BUCKET/$OUTPUT_S3_OBJECT_KEY

# Unset CodePipeline creds
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

unzip $BUILDER_HOME/tmp/source.zip -d $WORKSPACE

cd $WORKSPACE

if [ -e $WORKSPACE/build.sh ]
then
    $WORKSPACE/build.sh
fi

if [ ! -e $WORKSPACE/Dockerfile ]
then
    echo "Unable to find Dockerfile"
    exit 1
fi

docker build -t $IMAGE_NAME .
$(aws ecr get-login --region $AWS_DEFAULT_REGION)
docker push $IMAGE_NAME

echo "Build complete.."