#!/usr/bin/env python

import base64
import boto3
from botocore.client import Config

import datetime
import os
import json
import sys
import subprocess

PWD = os.getcwd()

# Setup constants
BUILDER_HOME = "/opt/builder"

# Get environment variables
CODEPIPELINE_ARTIFACT_CREDENTIALS = json.loads(os.environ['CODEPIPELINE_ARTIFACT_CREDENTIALS'])
CODEPIPELINE_USER_PARAMS          = json.loads(os.environ['CODEPIPELINE_USER_PARAMS'])
CODEPIPELINE_INPUT_ARTIFACTS      = json.loads(os.environ['CODEPIPELINE_INPUT_ARTIFACTS'])
CODEPIPELINE_OUTPUT_ARTIFACTS     = json.loads(os.environ['CODEPIPELINE_OUTPUT_ARTIFACTS'])

# Parse user parameters
user_params = dict()
pairs = CODEPIPELINE_USER_PARAMS.split(',')
for pair in pairs:
    kv = pair.split('=')
    user_params[ kv[0].strip() ] = kv[1].strip()

# Setup S3 client using CodePipeline provided credentials
cp_s3_client = boto3.client('s3',
                             config=Config(signature_version='s3v4'),
                             region_name=user_params['awsRegion'],
                             aws_access_key_id=CODEPIPELINE_ARTIFACT_CREDENTIALS['accessKeyId'],
                             aws_secret_access_key=CODEPIPELINE_ARTIFACT_CREDENTIALS['secretAccessKey'],
                             aws_session_token=CODEPIPELINE_ARTIFACT_CREDENTIALS['sessionToken'])

# Get input & output artifact names
inputArtifactName  = user_params['inputArtifactName']
outputArtifactName = user_params['outputArtifactName']

inputArtifact = None
inputArtifacts  = CODEPIPELINE_INPUT_ARTIFACTS
for artifact in inputArtifacts:
    if artifact['name'] == inputArtifactName:
        inputArtifact = artifact
        break

outputArtifact = None    
outputArtifacts = CODEPIPELINE_OUTPUT_ARTIFACTS
for artifact in outputArtifacts:
    if artifact['name'] == outputArtifactName:
        outputArtifact = artifact
        break

# Setup workspace
WORKSPACE = BUILDER_HOME + "/workspace"
TMP_DIR = BUILDER_HOME + "/tmp"
os.makedirs(WORKSPACE)
os.makedirs(TMP_DIR)

# Copy source bundle
SRC_LOC = TMP_DIR + "/source.zip"
cp_s3_client.download_file(
                            inputArtifact['location']['s3Location']['bucketName'],
                            inputArtifact['location']['s3Location']['objectKey'],
                            SRC_LOC)

# Switch CWD to workspace directory
os.chdir(WORKSPACE)

# Unzip source bundle to workspace
subprocess.check_call([ "unzip", TMP_DIR + "/source.zip", "-d", WORKSPACE])

if os.path.exists(WORKSPACE + "/build.sh"):
    os.chdir(WORKSPACE)
    subprocess.check_call(WORKSPACE + "/build.sh")

if not os.path.exists(WORKSPACE + "/Dockerfile"):
    print "Unable to find Dockerfile in source bundle"
    sys.exit(1)

# Set tag name based on datetime
timestamp = datetime.datetime.now()
tag = timestamp.strftime('%Y%m%d%H%M%S')

# Set docker image name
image_name = "%s.dkr.ecr.%s.amazonaws.com/%s:%s" % (
                                                    user_params['awsAccountId'],
                                                    user_params['awsRegion'],
                                                    user_params['ecrRepository'],
                                                    tag)
# Run Docker build
subprocess.check_call([ "docker", "build", "-t", image_name, "."])

# Run Docker login
ecr_client = boto3.client('ecr',
                          region_name=user_params['awsRegion'])

ecr_auth_data = ecr_client.get_authorization_token()['authorizationData'][0]

ecr_user = base64.b64decode(ecr_auth_data['authorizationToken']).split(':')[0]
ecr_token = base64.b64decode(ecr_auth_data['authorizationToken']).split(':')[1]

subprocess.check_call(["docker",
                        "login",
                        "-u", ecr_user,
                        "-p", ecr_token,
                        "-e", "none",
                        ecr_auth_data['proxyEndpoint']])

subprocess.check_call(["docker", "push", image_name])


# Send output
open('/tmp/output_image_name').write(image_name)
image_name_data = open('/tmp/output_image_name', 'rb')
cp_s3_client.put_object(Body=image_name_data,
                        Bucket=outputArtifact['location']['s3Location']['bucketName'],
                        Key=outputArtifact['location']['s3Location']['objectKey'],
                        ServerSideEncryption='aws:kms')

print "--- BUILD FINISHED ---"

os.chdir(PWD)