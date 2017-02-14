#!/usr/bin/env python2.7
"""
Tag RDS Clusters for cost allocations


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


NOTES: 

1. Use BOTO's AWS_ environment variables for credentials. 
   Or better, yet, if running from an EC2 instance: USE AN IAM ROLE. 

2. AWS EC2 API policy Allow permissions required: TODO

"""

import sys
import json
from boto import rds2

DEFAULT_REGION = 'us-east-1'

region = DEFAULT_REGION

# Positional arguments
# 1. AWS region
if sys.argv[1:]:
    region = sys.argv.pop(1)

# the ARN is the RDS identifier to use with rds2 objects
# but, we'll use the Name tag to filter
rds_names = list(sys.argv[1:])

regions = rds2.regions()
rds = rds2.connect_to_region(region)

if rds_arns:
  dbs = rds.describe_db_instances()
else
  dbs = rds.describe_db_instances()


for instance in dbs['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances']:

  #instance['DBInstanceIdentifier']
  #instance['DBInstanceStatus']
  #instance['Endpoint']

force_tagging = False

for snapshot in snapshots:
    rds.add_tags_to_resource

    snap_tags = ec2.get_all_tags(filters={
                'resource-id': snapshot.id, 
                'resource-type': 'snapshot'})

    is_named = False
    snap_name = "unnamed"
    is_tagged = False
    lincx_env = None
    lincx_type = None
    for tag in snap_tags:
        if tag.name == "Name":
            snap_name = tag.value
            is_named = True
        elif tag.name == "lincx_environment":
            lincx_env = tag.value
            is_tagged = True
        elif tag.name == "lincx_type":
            lincx_type = tag.value
            is_tagged = True

    if is_tagged:
      print "SNAPSHOT TAGGED:", snapshot.id, snap_name, lincx_env, lincx_type
      if not force_tagging:
          continue
    print "SNAPSHOT TAGGING:", snapshot.id, snap_name    
    ec2.create_tags([snapshot.id], tags={
                    'lincx_environment':'legacy',
                    'lincx_type':''})

# vim: set tabstop=4 shiftwidth=4 softtabstop=0 textwidth=0 expandtab :
