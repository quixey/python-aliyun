#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2014, Quixey Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""

ali: Aliyun commandline tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ali to hand-craft API requests to Aliyun's ECS and SLB APIs. Use Repeated
Key=Value arguments as described in the API documentation. To use more complex 
data structures, use JSON-formatted Values and enclose the entire Key=Value in 
single quotes.

**Usage:**

.. program-output:: ali.py --help

**Usage Example:**

.. code-block:: bash

    ali.py --region=cn-hangzhou --log-level=debug ecs Action=DescribeInstanceStatus
    {   
        "InstanceStatuses":{
            "InstanceStatus":[
                {   
                    "InstanceId":"AYinstanceid",
                    "Status":"Running"
                },
                {   
                    "InstanceId":"AYinstanceid",
                    "Status":"Running"
                },
                {   
                    "InstanceId":"AYinstanceid",
                    "Status":"Running"
                },
                {   
                    "InstanceId":"AYinstanceid",
                    "Status":"Running"
                }
            ]
        },
        "PageNumber":1,
        "PageSize":10,
        "RequestId":"....",
        "TotalCount":4
    }

"""


import aliyun.connection
import argparse
import json
import logging


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Ali Cloud (aliyun) API commandline tool.')
    parser.add_argument('-k', '--access-key-id', help='access key id')
    parser.add_argument('-s', '--secret-access-key', help='secret access key')
    parser.add_argument('-r', '--region_id', help='region id to connect to')
    parser.add_argument('--log-level', default='INFO')
    parser.add_argument('-S', '--service', help='the API service to use.', choices=['ecs', 'slb'])
    parser.add_argument('remainder', nargs='+')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    c = aliyun.connection.Connection(args.region_id, args.service,
                          access_key_id=args.access_key_id,
                          secret_access_key=args.secret_access_key)

    # Take all other params that are key value and make request params.
    params = dict([tuple(arg.split('=')) for arg in args.remainder if '=' in arg])

    result = c.get(params)
    print json.dumps(result, indent=4, sort_keys=True, separators=(',',':'), ensure_ascii=False)

