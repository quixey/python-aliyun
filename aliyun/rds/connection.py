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

import json
import datetime
import logging

import dateutil.parser

from aliyun.connection import Connection
from aliyun.rds.model import (
    RDSInstanceStatus,
    RDSInstance
)

BLOCK_TILL_RUNNING_SECS = 600

logger = logging.getLogger(__name__)

class Error(Exception):

    """Base exception class for this module."""


class RdsConnection(Connection):
    """A connection to Aliyun RDS service.

    Args:
        region_id (str): The id of the region to connect to.
        access_key_id (str): The access key id.
        secret_access_key (str): The secret access key.
    """
    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        super(RdsConnection, self).__init__(
	    region_id, 'rds', access_key_id=access_key_id,
	    secret_access_key=secret_access_key)
    
    def describe_all_db_instances(self, region_id='cn-hangzhou', engine=None, db_instance_type=None, instance_network_type=None, connection_mode=None):
        """
        Get the list of all RDS instances OR the list of RDS instances that are authorized by RAM.
	    Args:
	        region_id (str): The id of the region to connect to.
	        engine (str): Database type, MySQL/SQLServer/PostgreSQL/PPAS
	        db_instance_type (str): Instance type, Primary/Readonly/Guard/Temp
	        instance_network_type (str): Network type, VPC/Classic
	        connection_mode (str): values are in Performance/Safty
	
	    Returns:
        """
        dbinstance_status = []
        params = {'Action': 'DescribeDBInstances',
                'RegionId': self.region_id,
        }
        if engine:
            params['Engine'] = engine
        if db_instance_type:
            params['DBInstanceType'] = db_instance_type
        if instance_network_type:
            params['InstanceNetworkType'] = instance_network_type

        for item in self.get(params)['Items']['DBInstance']:
            dbinstance_status.append(RDSInstanceStatus(item['DBInstanceId'], item['DBInstanceStatus']))
        return dbinstance_status

    def get_all_dbinstance_ids(self, region_id=None):
        """Get all the instance ids in a region.

        Args:
            zone_id (str, optional): The Zone ID to get instance ids from.

        Returns:
            The list of instance ids.
        """
        return [x.instance_id for x in self.describe_all_db_instances(region_id)]

    def get_dbinstance(self, instance_id):
        """Get an rdsinstance.

        Args:
            instance_id (str): The id of the instance.

        Returns:
            :class:`.model.RdsInstance` if found.

        Raises:
            Error: if not found.
        """
        resp = self.get({
            'Action': 'DescribeDBInstanceAttribute',
            'DBInstanceId': instance_id})['Items']['DBInstanceAttribute'][0]
        return RDSInstance(
            resp['DBInstanceId'],
            resp['RegionId'],
            resp['DBInstanceClass'],
            resp['DBInstanceDescription'],
            resp['DBInstanceStatus'],
            resp['SecurityIPList'],
            resp['CreationTime'],
            resp['ExpireTime'],
            resp['PayType'],
            resp['ConnectionString'],
            resp['DBInstanceNetType'],
            resp['MaxConnections'],
            resp['Engine'],
            resp['AvailabilityValue'],
            resp['AccountMaxQuantity'],
            resp['DBMaxQuantity'],
            resp['DBInstanceMemory'],
            resp['MaxIOPS'],
            resp['DBInstanceType'],
            resp['EngineVersion'],
            resp['DBInstanceStorage'],
            resp['Port'])

    def report_expiring_dbinstance(self, days=7):
        """Report PrePaid RDS instances that are about to expire in <days>.
        Args:
        days (int): Check instances that will expire in <days>.
        """
        expiring_instances = []
        all_instances = self.get_all_dbinstance_ids()
        for ins in all_instances:
            res = self.get_dbinstance(ins)
            if res.instance_charge_type == 'Prepaid':
                expire_time = datetime.datetime.strptime(res.expired_time, "%Y-%m-%dT%H:%M:%SZ")
                now = datetime.datetime.now()
                if (expire_time - now).days <= days:
                    expiring_instances.append(ins)
        return expiring_instances
