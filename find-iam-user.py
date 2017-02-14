#!/usr/bin/env python2.7
"""

 Find the IAM username belonging to the TARGET_ACCESS_KEY
 Useful for finding IAM user corresponding to a compromised AWS credential


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


Requirements:
 python:

    boto # TODO: switch to boto3

 Boto Environment variables: 

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   or
    AWS_PROFILE


"""
import sys
import boto.iam

TARGET_ACCESS_KEYS = sys.argv[1:]

iam = boto.connect_iam()

users = iam.get_all_users('/')['list_users_response']['list_users_result']['users']

def find_key(access_key):
    for user in users:
        for key_result in iam.get_all_access_keys(user['user_name'])['list_access_keys_response']['list_access_keys_result']['access_key_metadata']:
            aws_access_key = key_result['access_key_id']
            if aws_access_key == access_key:
                print access_key + ' : ' + user['user_name']
                return True
    return False

for access_key in TARGET_ACCESS_KEYS:
    if not find_key(access_key):
        print access_key + ' : NOT_FOUND'
