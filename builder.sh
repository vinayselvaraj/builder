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

# Store creds
CP_AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
CP_AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
CP_AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN


# Install dependencies
yum -y install unzip

BUILDER_HOME=/opt/builder
WORKSPACE=$BUILDER_HOME/workspace

mkdir -p $BUILDER_HOME/tmp
mkdir -p $WORKSPACE

# Enable SigV4
aws configure set s3.signature_version s3v4
aws s3 cp s3://$INPUT_S3_BUCKET/$INPUT_S3_OBJECT_KEY $BUILDER_HOME/tmp/source.zip

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

IMAGE_NAME=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG

docker build -t $IMAGE_NAME .
$(aws ecr get-login --region $AWS_DEFAULT_REGION)
docker push $IMAGE_NAME

# Set CodePipeline creds
export AWS_ACCESS_KEY_ID=$CP_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$CP_AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN=$CP_AWS_SESSION_TOKEN

TMPFILE=`mktemp`
echo $IMAGE_NAME > $TMPFILE
aws s3 cp $TMPFILE s3://$OUTPUT_S3_BUCKET/$OUTPUT_S3_OBJECT_KEY

echo "Build complete.."