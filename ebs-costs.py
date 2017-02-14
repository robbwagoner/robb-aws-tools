#!/usr/bin/env python2.7
"""
Get an approximate cost of EBS for a Region, differentiating used (attached) 
vs. unused (available) EBS volumes, and their type (standard & gp2 vs. io1).


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

1. Howto calculate Snapshot costs is TBD. S3 is _cheap_ and snapshots are
   differential (generally small): it isn't a priority. 
2. Use BOTO's AWS_ environment variables for credentials. Or better, yet, if
   running from an EC2 instance: USE AN IAM ROLE. AWS ec2 policy required: 
   TBD
"""

import sys
import json
from boto import ec2

DEFAULT_REGION = 'us-east-1'

# http://aws.amazon.com/ebs/pricing/
EBS_PRICING = dict()

EBS_PRICING['us-east-1'] = {
    'gp2_gb': 0.1,
    'io1_gb': 0.125,
    'io1_iops': 0.065,
    'standard_gb': 0.05,
    'standard_1m_io': 0.05,
    'snapshot_gb': 0.095
}

EBS_PRICING['us-west-1'] = {
    'gp2_gb': 0.12,
    'io1_gb': 0.138,
    'io1_iops': 0.072,
    'standard_gb': 0.08,
    'standard_1m_io': 0.08,
    'snapshot_gb': 0.105
}

region = DEFAULT_REGION

# Positional arguments
# 1. AWS region
if sys.argv[1:]:
    region = sys.argv.pop(1)

def volume_price(volume, region):
    ''' get the price per hour for a given volume
    '''
    if volume.type == 'standard':
      return round(EBS_PRICING[region]['standard_gb'] * volume.size,2)
    if volume.type == 'gp2':
      return round(EBS_PRICING[region]['gp2_gb'] * volume.size,2)
    if volume.type == 'io1':
      return round(EBS_PRICING[region]['io1_gb'] * volume.size,2)

# accumlating the costs
vol_costs = dict(
    total = 0.0,            # total costs for all EBS
    total_unused_gb = 0.0,  # costs for unused standard and gp2 EBS
    total_unused_io = 0.0,  # costs for unused PIOPS IO
    total_unused_io_gb = 0.0, # costs for unused PIOPS storage
    count = 0,              # count of EBS volumes
    count_unused = 0,       # count of unused standard and gp2 EBS volumes
    count_io_unused = 0     # count of unused PIOPS EBS volumes
    )

print "Getting EBS costs for region {0}".format(region)
ec2 = ec2.connect_to_region(region)
vols = ec2.get_all_volumes()
vol_costs['count'] = len(vols)

for vol in vols:
    price_gb = volume_price(vol, region)
    price_io = 0
    if vol.type == 'io1':
        price_io = round(vol.iops * EBS_PRICING[region]['io1_iops'],2)

    vol_costs['total'] += (price_gb + price_io)

    # Is the volume unused?
    attach_data = vol.attach_data

    if not attach_data.status:
        if vol.type == 'io1':
            vol_costs['total_unused_io_gb'] += price_gb
            vol_costs['total_unused_io'] += price_io
            vol_costs['count_io_unused'] += 1
        else:
            vol_costs['total_unused_gb'] += price_gb
            vol_costs['count_unused'] += 1

total_unused_io_cost = round((vol_costs['total_unused_io'] + vol_costs['total_unused_io_gb']),2)

# ----------
# Snapshots
# ----------
snap_costs = dict(
    total = 0.0,
    count = 0
    )

def get_snapshots():
    snaps = ec2.get_all_snapshots(owner='self')
    snap_costs['count'] = len(snaps)
    for snap in snaps:
        snap_cost = round(snap.volume_size * EBS_PRICING[region]['snapshot_gb'], 2)
        snap_costs['total'] += snap_cost
        #print "{0}: {1}".format(snap.owner_alias, snap.owner_id)


print "Volumes: {0}".format(vol_costs['count'])
print "Cost ($/month): {0}".format(vol_costs['total'])
print "Unused std/gp2 volumes (count): {0}".format(vol_costs['count_unused'])
print "Unused std/gp2 cost ($/month): {0}".format(vol_costs['total_unused_gb'])
print "Unused PIOPS volumes: {0}".format(vol_costs['count_io_unused'])
print "Unused PIOPS cost ($/month): {0}".format(total_unused_io_cost)
#print "Total EBS Snapshots cost ($/month): {0}".format(snap_costs['total'])
#print json.dumps(vol_costs)

# vim: set tabstop=4 shiftwidth=4 softtabstop=0 textwidth=0 expandtab :
