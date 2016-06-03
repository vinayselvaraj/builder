#!/usr/bin/env python

import boto3
import datetime
import os
import json

# Setup constants
BUILDER_HOME = "/opt/builder"

# Get environment variables
CODEPIPELINE_ARTIFACT_CREDENTIALS = json.loads(os.environ['CODEPIPELINE_ARTIFACT_CREDENTIALS'])
CODEPIPELINE_USER_PARAMS          = json.loads(os.environ['CODEPIPELINE_USER_PARAMS'])
CODEPIPELINE_INPUT_ARTIFACTS      = json.loads(os.environ['CODEPIPELINE_INPUT_ARTIFACTS'])
CODEPIPELINE_OUTPUT_ARTIFACTS     = json.loads(os.environ['CODEPIPELINE_OUTPUT_ARTIFACTS'])

print CODEPIPELINE_ARTIFACT_CREDENTIALS
print CODEPIPELINE_INPUT_ARTIFACTS
print CODEPIPELINE_OUTPUT_ARTIFACTS

# Parse user parameters
user_params = dict()
pairs = CODEPIPELINE_USER_PARAMS.split(',')
for pair in pairs:
    kv = pair.split('=')
    user_params[ kv[0].strip() ] = kv[1].strip()

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
os.mkdir(WORKSPACE)
os.mkdir(TMP_DIR)

# Copy source bundle to TMP_DIR


