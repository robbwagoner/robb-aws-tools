#!/usr/bin/env python2.7
"""
Simplistic RDS logfile downloader because AWS CLI + Botocore is broken. :-(

  https://github.com/aws/aws-cli/issues/1504

Copyright 2017 Robb Wagoner robb.wagoner@gmail.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import print_function

import argparse
import os.path
import sys

import boto3
from botocore.exceptions import NoRegionError, ClientError

__author__ = 'robbwagoner'
__email__ = 'robb.wagoner@gmail.com'

parser = argparse.ArgumentParser(description='Simplistic RDS logfile downloader')
parser.add_argument('--region')
parser.add_argument('--rds-instance', required=True, help='The RDS name')
parser.add_argument('--rds-log-file', required=True, help='The log file to download')
parser.add_argument('--local-log-file', help='The path where to place the log file on the local file system')

args = parser.parse_args()
region = args.region
rds_instance = args.rds_instance
log_file = args.rds_log_file

if args.local_log_file:
    local_log_file = args.local_log_file
else:
    local_log_file = os.path.basename(log_file)

try:
    rds = boto3.client('rds', region)
except NoRegionError:
    rds = boto3.client('rds','us-east-1')

with open(local_log_file, 'w') as f:
    sys.stdout.write('downloading {rds} log file {file}\n'.format(rds=rds_instance, file=log_file))
    token = '0'
    try:
        response = rds.download_db_log_file_portion(
            DBInstanceIdentifier=rds_instance,
            LogFileName=log_file,
            Marker=token)
        f.write(response['LogFileData'])
        while response['AdditionalDataPending']:
            token=response['Marker']
            response = rds.download_db_log_file_portion(
                DBInstanceIdentifier=rds_instance,
                LogFileName=log_file,
                Marker=token)
            f.write(response['LogFileData'])
        sys.stdout.write('done: {}\n'.format(local_log_file))
    except ClientError as e:
        print(e)
        sys.exit(2)
