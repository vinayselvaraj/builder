#!/usr/bin/env python

import os
import json

def main():
    
    # Get environment variables
    CODEPIPELINE_ARTIFACT_CREDENTIALS = json.loads(os.environ['CODEPIPELINE_ARTIFACT_CREDENTIALS'])
    CODEPIPELINE_USER_PARAMS          = json.loads(os.environ['CODEPIPELINE_USER_PARAMS'])
    CODEPIPELINE_INPUT_ARTIFACTS      = json.loads(os.environ['CODEPIPELINE_INPUT_ARTIFACTS'])
    CODEPIPELINE_OUTPUT_ARTIFACTS     = json.loads(os.environ['CODEPIPELINE_OUTPUT_ARTIFACTS'])
    
    print CODEPIPELINE_ARTIFACT_CREDENTIALS
    print CODEPIPELINE_USER_PARAMS
    print CODEPIPELINE_INPUT_ARTIFACTS
    print CODEPIPELINE_OUTPUT_ARTIFACTS

if __name__ == "__main__":
    main()