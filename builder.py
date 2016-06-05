#!/usr/bin/env python

import boto3
from botocore.client import Config

import datetime
import os
import json
import sys
import zipfile
import subprocess

# Setup constants
BUILDER_HOME = "/opt/builder"

# Get environment variables
CODEPIPELINE_ARTIFACT_CREDENTIALS = json.loads(os.environ['CODEPIPELINE_ARTIFACT_CREDENTIALS'])
CODEPIPELINE_USER_PARAMS          = json.loads(os.environ['CODEPIPELINE_USER_PARAMS'])
CODEPIPELINE_INPUT_ARTIFACTS      = json.loads(os.environ['CODEPIPELINE_INPUT_ARTIFACTS'])
CODEPIPELINE_OUTPUT_ARTIFACTS     = json.loads(os.environ['CODEPIPELINE_OUTPUT_ARTIFACTS'])

print os.environ['CODEPIPELINE_ARTIFACT_CREDENTIALS']
print os.environ['CODEPIPELINE_USER_PARAMS']
print os.environ['CODEPIPELINE_INPUT_ARTIFACTS']
print os.environ['CODEPIPELINE_OUTPUT_ARTIFACTS']

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

print "inputArtifact: %s" % inputArtifact
print "outputArtifact: %s" % outputArtifact

# Set tag name based on datetime
timestamp = datetime.datetime.now()
tag = timestamp.strftime('%Y%m%d%H%M%S')

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

# Unzip source bundle to workspace
zf = zipfile.ZipFile(TMP_DIR + "/source.zip")
zf.extractall(WORKSPACE)
zf.close()

print "Running: ls %s" % BUILDER_HOME
subprocess.call("ls %s" % BUILDER_HOME)

print "Running: ls %s" % WORKSPACE
subprocess.call("ls %s" % WORKSPACE)

if os.path.exists(WORKSPACE + "/build.sh"):
    subprocess.check_call(WORKSPACE + "/build.sh")

if not os.path.exists(WORKSPACE + "/Dockerfile"):
    print "Unable to find Dockerfile in source bundle"
    sys.exit(1)

