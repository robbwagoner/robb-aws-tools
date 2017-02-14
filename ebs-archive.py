#!/usr/bin/env python2.7
"""
Archive (snapshot) unused (available) EBS volumes.
Volumes and Snapshots are tagged: 'archived'='yes'.
Volumes are otherwise untouched. I.e. they are NOT DELETED.

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
import datetime
from boto import ec2

DEFAULT_REGION = 'us-east-1'


snapshot_description_archive = 'EBS ARCHIVE FINAL SNAPSHOT 2015-02-13 by robb@pandastrike.com'

region = DEFAULT_REGION

# Positional arguments
# 1. AWS region
if sys.argv[1:]:
    region = sys.argv.pop(1)

vols = list(sys.argv[1:])

ec2 = ec2.connect_to_region(region)

do_archive = True       # do archival snapshots
available_only = True   # snapshot only those volumes which 
                        #     are available (unattached)


if vols:
  volumes = ec2.get_all_volumes(volume_ids=vols)
else:
  volumes = ec2.get_all_volumes()

snapshots = ec2.get_all_snapshots(owner='self')

for volume in volumes:
    if available_only:
        if  volume.attach_data.status:
            print "SKIPPING: Attached volume", volume.id
            continue

    vol_tags = ec2.get_all_tags(filters={'resource-id': volume.id, 'resource-type': 'volume'})

    is_archived = False
    is_named = False
    vol_name = 'unnamed'
    for tag in vol_tags:
        if tag.name == 'Name':
            vol_name = tag.value
            is_named = True
        elif tag.name == 'archived' and tag.value == 'yes':
            is_archived = True
        
    if is_archived:
        print "SKIPPING: Already archived:", volume.id, vol_name
        continue

    if do_archive:
        print "ARCHIVING:",volume.id, vol_name
        snap_description = "{0} - {1}".format(vol_name, snapshot_description_archive)
    else:
        snap_description = "{0} - created by robb@pandastrike".format(vol_name)

    # do snapshot
    print "Creating snapshot for volume {0}: '{1}'.".format(volume.id,snap_description)
    snapshot = volume.create_snapshot(description=snap_description)
    if do_archive:
        ec2.create_tags([volume.id, snapshot.id], tags={'archived':'yes'})

# vim: set tabstop=4 shiftwidth=4 softtabstop=0 textwidth=0 expandtab :
