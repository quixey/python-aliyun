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

from aliyun.connection import Connection, Error
from aliyun.ess.model import (
    ScalingGroup,
    ScalingConfiguration
    )

import dateutil.parser
import time


class EssConnectionError(Error):
    """Base exception class for aliyun.ess.connection"""


class EssConnection(Connection):
    """A connection to Aliyun ESS service.

    Args:
        region_id (str): The id of the region to connect to.
        access_key_id (str): The Aliyun API Access Key ID.
        secret_access_key (str): The Aliyun API Secret Access Key
    """

    ACTIONS = [
        'CreateScalingGroup',
        'ModifyScalingGroup',
        'DescribeScalingGroups',
        'EnableScalingGroup',
        'DisableScalingGroup',
        'DeleteScalingGroup',
        'DescribeScalingInstances',
        'CreateScalingConfiguration',
        'DescribeScalingConfigurations',
        'DeleteScalingConfigurations',
        'CreateScalingRule',
        'ModifyScalingRule',
        'DescribeScalingRules',
        'DeleteScalingRule',
        'ExecuteScalingRule',
        'AttachInstances',
        'RemoveInstances',
        'CreateScheduledTask',
        'ModifyScheduledTask',
        'DescribeScheduledTasks',
        'DeleteScheduledTask',
        'DescribeScalingActivities'
    ]

    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        super(EssConnection, self).__init__(
            region_id, 'ess', access_key_id=access_key_id,
            secret_access_key=secret_access_key)

    def create_scaling_group(self, max_size, min_size,
                             scaling_group_name=None, default_cooldown=None,
                             removal_policies=None, load_balancer_id=None,
                             db_instance_ids=None):
        """Create a scaling group.

        Create a collection of ECS instances with a minimum and maximum number.
        A load balancer and multiple database instances can be kept in-sync
        with the changes in the instances.

        Args:
            max_size (int): Maximum number of ECS instances. Between 0 and 100.
            min_size (int): Minimum number of ECS instances. Between 0 and 100.
            scaling_group_name (str): Name of the scaling group.
            default_cooldown (int): Number of seconds to wait between scaling
                activities. Between 0 and 86400, ESS default of 300.
            removal_policies (list): List of removal policies. Choices are:
                OldestInstance, NewestInstance, OldestScalingConfiguration.
                ESS default is ['OldestScalingConfiguration', 'OldestInstance']
            load_balancer_id (str): ID of associated
                :class:`aliyun.slb.model.LoadBalancer`.
            db_instance_ids (list): List of up to 3 RDS database instances.
        """
        params = {
            'Action': 'CreateScalingGroup',
            'MaxSize': max_size,
            'MinSize': min_size
        }

        if scaling_group_name:
            params['ScalingGroupName'] = scaling_group_name
        if default_cooldown:
            params['DefaultCooldown'] = default_cooldown
        if removal_policies and isinstance(removal_policies, list):
            for n, policy in enumerate(removal_policies):
                params['RemovalPolicy.' + str(n+1)] = policy
        if load_balancer_id:
            params['LoadBalancerId'] = load_balancer_id
        if db_instance_ids and isinstance(db_instance_ids, list):
            for n, db in enumerate(db_instance_ids):
                params['DBInstanceId.' + str(n+1)] = db

        return self.get(params)

    def modify_scaling_group(self, scaling_group_id, scaling_group_name=None,
                             active_scaling_configuration_id=None,
                             min_size=None, max_size=None,
                             default_cooldown=None, removal_policies=None):
        '''Modify an existing Scaling Group.

        Adjust an existing scaling group's name, configuration, size, cooldown,
        or removal policy. Leave parameters blank to leave the value unchanged
        in the scaling group.

        Args:
            scaling_group_id (str): ID of the ScalingGroup to modify.
            scaling_group_name (str): New name of the scaling group.
            active_scaling_configuration_id (str): ID of the desired
                configuration.
            min_size (int): The new minimum size.
            max_size (int): The new maximum size.
            default_cooldown (int): The new time between scaling activities.
            removal_policies (list): The new list of instance removal policies.
        '''
        params = {
            'Action': 'ModifyScalingGroup',
            'ScalingGroupId': scaling_group_id
        }
        if scaling_group_name:
            params['ScalingGroupName'] = scaling_group_name
        if active_scaling_configuration_id:
            params['ActiveScalingConfigurationId'] = active_scaling_configuration_id  # NOQA
        if min_size:
            params['MinSize'] = min_size
        if max_size:
            params['MaxSize'] = max_size
        if default_cooldown:
            params['DefaultCooldown'] = default_cooldown
        if removal_policies and isinstance(removal_policies, list):
            for n, policy in enumerate(removal_policies):
                params['RemovalPolicy.' + str(n+1)] = policy

        return self.get(params)

    def describe_scaling_groups(self, scaling_group_ids=None,
                                scaling_group_names=None):
        '''Describe scaling groups, optionally with specific IDs or names.

        Args:
            scaling_group_ids (list): List of scaling group IDs to find.
            scaling_group_names (list): List of scaling group names to find.

        Return: list of :class:`.model.ScalingGroup`'''

        params = {
            'Action': 'DescribeScalingGroups'
        }
        if scaling_group_ids and isinstance(scaling_group_ids, list):
            for n, scaling_group_id in enumerate(scaling_group_ids):
                params['ScalingGroupId.' + str(n+1)] = scaling_group_id

        if scaling_group_names and isinstance(scaling_group_names, list):
            for n, scaling_group_name in enumerate(scaling_group_names):
                params['ScalingGroupName.' + str(n+1)] = scaling_group_name
        groups = []
        for page in self.get(params, paginated=True):
            for g in page['ScalingGroups']['ScalingGroups']:
                groups.append(ScalingGroup(
                    scaling_group_id=g['ScalingGroupId'],
                    scaling_group_name=g['ScalingGroupName'],
                    active_scaling_configuration_id=g['ActiveScalingConfigurationId'],  # NOQA
                    region_id=g['RegionId'],
                    min_size=g['MinSize'],
                    max_size=g['MaxSize'],
                    default_cooldown=g['DefaultCooldown'],
                    removal_policies=g['RemovalPolicies']['RemovalPolicy'],
                    load_balancer_id=g['LoadBalancerId'],
                    db_instance_ids=g.get('DBInstanceIds', {}).get('DBInstanceId', None),
                    lifecycle_state=g['LifecycleState'],
                    total_capacity=g['TotalCapacity'],
                    active_capacity=g['ActiveCapacity'],
                    pending_capacity=g['PendingCapacity'],
                    removing_capacity=g['RemovingCapacity'],
                    creation_time=dateutil.parser.parse(g['CreationTime'])
                ))
        return groups

    def get_all_scaling_group_ids(self, scaling_group_ids=None,
                                  scaling_group_names=None):
        '''Get IDs of all existing scaling groups.

        This is a wrapper around :func:`.describe_scaling_groups`.

        Args:
            scaling_group_ids (list): Optional list of ids to find ids... for.
            scaling_group_names (list): Optional list of names to find ids for.

        Return: list of :class:`.model.ScalingGroup` IDs.'''

        groups = self.describe_scaling_groups(scaling_group_ids=scaling_group_ids,  # NOQA
                                              scaling_group_names=scaling_group_names)  # NOQA
        return [g.scaling_group_id for g in groups]


