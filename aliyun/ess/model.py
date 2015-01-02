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

class Region(object):
    """Aliyun ESS Region.

       Args:
           region_id (str): The id of the region.
           local_name (str): The local name of the region.
    """

    def __init__(self, region_id, local_name):
        self.region_id = region_id
        self.local_name = local_name

    def __repr__(self):
        return u'<Region %s (%s) at %s>' % (
            self.region_id, self.local_name, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class ScalingGroup(object):
    """Scaling Group for Aliyun ESS.

    Collection of automatically-managed ECS instances and their associations
    with SLB load balancer instances and RDS database instances.

    Args:
        scaling_group_id (str): Scaling Group ID from ESS.
        scaling_group_name (str): Name of the Scaling Group.
        active_scaling_configuration_id (str): ID of the associated
            :class:`.model.ScalingConfiguration`.
        region_id (str): ID of associated :class:`.model.Region`.
        min_size (int): Minimum number of ECS instances allowed.
        max_size (int): Maximum number of ECS instances allowed.
        default_cooldown (int): Number of seconds between scaling activities.
        removal_policies (list): List of removal policies. See
            :func:`.connection.EssConnection.create_scaling_group`.
        load_balancer_id (str): ID of associated :class:`aliyun.slb.model.LoadBalancer`.
        db_instance_ids (list): List of RDS DB Instance Ids
        lifecycle_state (str): Current lifecycle state. One of 'Inactive',
            'Active', or 'Deleting'.
        total_capacity (int): Total number of ECS instances managed in the
            scaling group.
        active_capacity (int): Number of ECS instances attached and running in
            the scaling group.
        pending_capacity (int): Number of ECS instances joining the group.
        removing_capacity (int): Number of ECS instances leaving the group and
            being released.
        creation_time (datetime): Time the scaling group was created.
    """

    def __init__(self, scaling_group_id, scaling_group_name,
            active_scaling_configuration_id, region_id, min_size, max_size,
            default_cooldown, removal_policies, db_instance_ids,
            load_balancer_id):

        self.scaling_group_id = scaling_group_id   
        self.scaling_group_name = scaling_group_name
        self.active_scaling_configuration_id = active_scaling_configuration_id
        self.region_id = region_id
        self.min_size = min_size
        self.max_size = max_size
        self.default_cooldown = default_cooldown
        self.removal_policies = removal_policies
        self.load_balancer_id = load_balancer_id
        self.db_instance_ids = db_instance_ids
        self.lifecycle_state = lifecycle_state
        self.total_capacity = total_capacity
        self.active_capacity = active_capacity
        self.pending_capacity = pending_capacity
        self.removing_capacity = removing_capacity
        self.creation_time = creation_time

    def __repr__(self):
        return u'<ScalingGroup {name} ({id}) at {mem}'.format(
            name=self.scaling_group_name,
            id=self.scaling_group_id,
            mem=id(self)
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class ScalingConfiguration(object):
    def __init__(self):
        pass
