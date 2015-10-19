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
import time
import datetime
import logging

import dateutil.parser

from aliyun.connection import Connection
from aliyun.ecs.model import (
    AutoSnapshotPolicy,
    AutoSnapshotExecutionStatus,
    AutoSnapshotPolicyStatus,
    Disk,
    DiskMapping,
    Image,
    Instance,
    InstanceStatus,
    InstanceType,
    Region,
    SecurityGroup,
    SecurityGroupInfo,
    SecurityGroupPermission,
    Snapshot,
    Zone
)

BLOCK_TILL_RUNNING_SECS = 600

logger = logging.getLogger(__name__)

class Error(Exception):

    """Base exception class for this module."""


class EcsConnection(Connection):

    """A connection to Aliyun ECS service.

    Args:
        region_id (str): The id of the region to connect to.
        access_key_id (str): The access key id.
        secret_access_key (str): The secret access key.
    """

    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        super(EcsConnection, self).__init__(
            region_id, 'ecs', access_key_id=access_key_id,
            secret_access_key=secret_access_key)

    def get_all_regions(self):
        """Get all regions.

        Returns:
            list: A list of :class:`aliyun.ecs.model.Region`
        """
        resp = self.get({'Action': 'DescribeRegions'})
        regions = []
        for region in resp['Regions']['Region']:
            regions.append(Region(region['RegionId'], region['LocalName']))
        return regions

    def get_all_region_ids(self):
        """Get all the region ids.

        Returns:
            List of region ids.
        """
        return [x.region_id for x in self.get_all_regions()]

    def get_all_zones(self):
        """Get all availability zones in the region.

        Returns:
            List of :class:`.model.Zone`.
        """
        resp = self.get({'Action': 'DescribeZones'})
        zones = []
        for zone in resp['Zones']['Zone']:
            zid = zone['ZoneId']
            zname = zone['LocalName']
            resources = zone['AvailableResourceCreation']['ResourceTypes']
            disks = zone['AvailableDiskCategories']['DiskCategories']
            zones.append(Zone(zid, zname, resources, disks))
        return zones

    def get_all_zone_ids(self):
        """Get all availability zone ids in the region.

        Returns:
            List of zone id strings.
        """
        return [z.zone_id for z in self.get_all_zones()]

    def get_all_clusters(self):
        """Get a list of ECS clusters in the region.

        Returns:
            List of cluster IDs.
        """
        params = {'Action': 'DescribeClusters'}
        clusters = []
        for cluster in self.get(params)['Clusters']['Cluster']:
            clusters.append(cluster['ClusterId'])
        return clusters

    def get_all_instance_status(self, zone_id=None):
        """Get the instance statuses.

        Args:
            zone_id (str, optional): A specific zone id to get instances from.

        Returns:
            The list of :class:`.model.InstanceStatus`.
        """
        instance_status = []
        params = {
            'Action': 'DescribeInstanceStatus'
        }

        if zone_id is not None:
            params.update({'ZoneId': zone_id})

        for resp in self.get(params, paginated=True):
            for item in resp['InstanceStatuses']['InstanceStatus']:
                instance_status.append(
                    InstanceStatus(item['InstanceId'], item['Status']))
        return instance_status

    def get_all_instance_ids(self, zone_id=None):
        """Get all the instance ids in a region.

        Args:
            zone_id (str, optional): The Zone ID to get instance ids from.

        Returns:
            The list of instance ids.
        """
        return [x.instance_id for x in self.get_all_instance_status(zone_id)]

    def get_instance(self, instance_id):
        """Get an instance.

        Args:
            instance_id (str): The id of the instance.

        Returns:
            :class:`.model.Instance` if found.

        Raises:
            Error: if not found.
        """
        resp = self.get({
            'Action': 'DescribeInstanceAttribute',
            'InstanceId': instance_id})
        return Instance(
            resp['InstanceId'],
            resp['InstanceName'],
            resp['ImageId'],
            resp['RegionId'],
            resp['InstanceType'],
            resp['HostName'],
            resp['Status'],
            [x for x in resp['SecurityGroupIds']['SecurityGroupId']],
            [x for x in resp['PublicIpAddress']['IpAddress']],
            [x for x in resp['InnerIpAddress']['IpAddress']],
            resp['InternetChargeType'],
            int(resp['InternetMaxBandwidthIn']),
            int(resp['InternetMaxBandwidthOut']),
            dateutil.parser.parse(resp['CreationTime']),
	    dateutil.parser.parse(resp['ExpiredTime']),
	    resp['InstanceChargeType'],
            resp['Description'],
            resp['ClusterId'],
            [x for x in resp['OperationLocks']['LockReason']],
            resp['ZoneId'])

    def start_instance(self, instance_id):
        """Start an instance.

        Args:
            instance_id (str): The id of the instance.
        """
        self.get({'Action': 'StartInstance',
                  'InstanceId': instance_id})

    def stop_instance(self, instance_id, force=False):
        """Stop an instance.

        Args:
            instance_id (str): The id of the instance.
            force (bool): Whether to force stop the instance.
        """
        self.get({'Action': 'StopInstance',
                  'InstanceId': instance_id,
                  'ForceStop': 'true' if force else 'false'})

    def reboot_instance(self, instance_id, force=False):
        """Reboot an instance.

        Args:
            instance_id (str): The id of the instance.
            force (bool): Whether to force reboot the instance.
        """
        self.get({'Action': 'RebootInstance',
                  'InstanceId': instance_id,
                  'ForceStop': 'true' if force else 'false'})

    def delete_instance(self, instance_id):
        """Delete an instance.

        Args:
            instance_id (str): The id of the instance.
        """
        self.get({'Action': 'DeleteInstance',
                  'InstanceId': instance_id})

    def modify_instance(self, instance_id, new_instance_name=None,
                        new_password=None, new_hostname=None,
                        new_security_group_id=None, new_description=None):
        """Modify certain attributes of an instance.

        Only attributes that you want to modify should be specified.
        If you want to associated multiple security groups with an instance
        use the join_security_group method.

        Args:
            instance_id (str): The id of the instance.
            new_instance_name (str): The new instance name.
            new_password (str): The new root password for the instance.
                This requires a reboot to take effect.
            new_hostname (str): The new hostname for the instance.
            new_security_group_id (str): A single security group id.
            new_description (str): The new description for the instance.
        """
        params = {'Action': 'ModifyInstanceAttribute',
                  'InstanceId': instance_id}
        if new_instance_name:
            params['InstanceName'] = new_instance_name
        if new_password:
            params['Password'] = new_password
        if new_hostname:
            params['HostName'] = new_hostname
        if new_security_group_id:
            params['SecurityGroupId'] = new_security_group_id
        if new_description:
            params['Description'] = new_description

        self.get(params)

    def modify_instance_spec(self, instance_id, instance_type=None,
                             internet_max_bandwidth_out=None,
                             internet_max_bandwidth_in=None):
        """NOT PUBLICLY AVAILABLE: Modify instance specification

        Modify an existing instance's instance type or in/out bandwidth limits.
        This API Action is restricted, so you may get an error when calling this
        method.

        Args:
            instance_id (str): The id fo the instance.
            instance_type (str): Use describe_instance_types for valid values.
            internet_max_bandwidth_out (int): Outbound bandwdith limit in Mbps.
                                              between 1 and 200, inclusive.
            internet_max_bandwidth_in (int): Inbound bandwdith limit in Mbps.
                                             between 1 and 200, inclusive.
        """
        params = {'Action': 'ModifyInstanceSpec',
                  'InstanceId': instance_id}

        if instance_type:
            params['InstanceType'] = instance_type
        if internet_max_bandwidth_out:
            params['InternetMaxBandwidthOut'] = internet_max_bandwidth_out
        if internet_max_bandwidth_in:
            params['InternetMaxBandwidthIn'] = internet_max_bandwidth_in

        self.get(params)

    def report_expiring_instance(self, days=7):
        """Report PrePaid instances that are about to expire in <days>.

	Args:
	    days (int): Check instances that will expire in <days>.
	"""
	# tzinfo has to be the same as the one in instance.expired_time
        # So we need to get it first, then provide it to now() as an arg
	expiring_instances = []
	all_instances = self.get_all_instance_ids()
	for ins in all_instances:
	    res = self.get_instance(ins)
	    if res.instance_charge_type == 'PrePaid':
	        """
		tzinfo has to be the same as the one in instance.expired_time
		So we need to get it first, then provide it to now() as an arg
		"""
		tz = res.expired_time.tzinfo
		now = datetime.datetime.now(tz)
	        if (res.expired_time - now).days <= days:
		    expiring_instances.append(ins)

	return expiring_instances

    def renew_instance(self, instance_id, period=None):
        """Renew an PrePaid Instance.

	Args:
	    instance_id (str): The id of the instance.
	    period (int): The period of renewing an Instance, in month. Valid values are,
	    							- 1 - 9
								- 12
								- 24
								- 36
	"""
	params = {'Action': 'RenewInstance',
	          'InstanceId': instance_id}
        
	if period is None:
	    exit('Period Must be supplied. Valid values are [1-9, 12, 24, 36]')
	params['Period'] = period

	self.get(params)

    def replace_system_disk(self, instance_id, image_id):
        """Replace an Instance's system disk to the given Image.

        Args:
            instance_id (str): ID of the Instance to replace.
            image_id (str): ID of the Image to use for the new system disk.

        Returns:
            ID of the new disk.
        """
        return self.get({
            'Action': 'ReplaceSystemDisk',
            'InstanceId': instance_id,
            'ImageId': image_id
            })['DiskId']

    def join_security_group(self, instance_id, security_group_id):
        """Add an instance to a security group.

        Args:
            instance_id (str): The id of the instance.
            security_group_id (str): The id of the security_group.
        """
        self.get({'Action': 'JoinSecurityGroup',
                  'InstanceId': instance_id,
                  'SecurityGroupId': security_group_id})

    def leave_security_group(self, instance_id, security_group_id):
        """Remove an instance from a security group.

        Args:
            instance_id (str): The id of the instance.
            security_group_id (str): The id of the security_group.
        """
        self.get({'Action': 'LeaveSecurityGroup',
                  'InstanceId': instance_id,
                  'SecurityGroupId': security_group_id})

    def create_disk(self, zone_id, name=None, description=None, size=None,
                    snapshot_id=None):
        """Create a non-durable disk.
        A new disk will be created and can be managed independently of instance.

        Either size or snapshot_id must be specified, but not both. If
        snapshot_id is specified, the size will be taken from the snapshot.

        If the snapshot referenced was created before 15 July, 2013, the API
        will throw an error of InvalidSnapshot.TooOld.

        Args:
            zone_id (str): the Availability Zone to create the disk in. This is
                           required and cannot be changed. E.g. cn-hangzhou-a.
            name (str): A short name for the disk.
            description (str): A longer description of the disk.
            size (int): Size of the disk in GB. Must be in the range [5-2048].
            snapshot_id (str): The snapshot ID to create a disk from.
                               If used, the size will be taken from the snapshot
                               and the given size will be disregarded.

        Returns:
            (str): The ID to reference the created disk.
        """
        if size is not None and snapshot_id is not None:
            raise Error("Use size or snapshot_id. Not both.")

        params = {
            'Action': 'CreateDisk',
            'ZoneId': zone_id
        }

        if size is not None:
            params['Size'] = size

        if snapshot_id is not None:
            params['SnapshotId'] = snapshot_id

        if name is not None:
            params['DiskName'] = name

        if description is not None:
            params['Description'] = description

        return self.get(params)['DiskId']

    def attach_disk(self, instance_id, disk_id, device=None,
                    delete_with_instance=None):
        """Attach an existing disk to an existing instance.
        The disk and instance must already exist. The instance must be in the
        Stopped state, or the disk will be attached at next reboot.

        The disk will be attached at the next available drive letter (e.g.
        in linux, /dev/xvdb if only /dev/xvda exists). It will be a raw and
        un-formatted block device.

        Args:
            instance_id (str): ID of the instance to add the disk to.
            disk_id (str): ID of the disk to delete.
            device (str): The full device path for the attached device. E.g.
                          /dev/xvdb. Valid values: /dev/xvd[b-z].
            delete_with_instance (bool): Whether to delete the disk when its
                                         associated instance is deleted.
        """

        params = {
            'Action': 'AttachDisk',
            'InstanceId': instance_id,
            'DiskId': disk_id
        }
        if device is not None:
            params['Device'] = device
        if delete_with_instance is not None:
            params['DeleteWithInstance'] = delete_with_instance

        self.get(params)

    def detach_disk(self, instance_id, disk_id):
        """Detach an existing disk from an existing instance.

        Args:
            instance_id (str): ID of the instance to add the disk to.
            disk_id (str): ID of the disk to delete.
        """

        self.get({
            'Action': 'DetachDisk',
            'InstanceId': instance_id,
            'DiskId': disk_id
            })

    def add_disk(self, instance_id, size=None, snapshot_id=None, name=None,
                 description=None, device=None, delete_with_instance=None):
        """Create and attach a non-durable disk to an instance.

        This is convenience method, combining create_disk and attach_disk.

        A new disk will be allocated for the instance and attached as the next
        available disk letter to the OS. The disk is a plain block device with
        no partitions nor filesystems.

        Either size or snapshot_id must be specified, but not both. If
        snapshot_id is specified, the size will be taken from the snapshot.

        If the snapshot referenced was created before 15 July, 2013, the API
        will throw an error of InvalidSnapshot.TooOld.

        Args:
            instance_id (str): ID of the instance to add the disk to.
            size (int): Size of the disk in GB. Must be in the range [5-2048].
            snapshot_id (str): The snapshot ID to create a disk from.
                               If used, the size will be taken from the snapshot
                               and the given size will be disregarded.
            name (str): A short name for the disk.
            description (str): A longer description of the disk.
            device (str): The full device path for the attached device. E.g.
                          /dev/xvdb. Valid values: /dev/xvd[b-z].
            delete_with_instance (bool): Whether to delete the disk when its

        Returns:
            disk_id (str): the ID to reference the created disk.

        Raises:
            Error: if size and snapshot_id are used.
            Error: InvalidSnapshot.TooOld if referenced snapshot is too old.

        """

        zone = self.get_instance(instance_id).zone_id
        disk = self.create_disk(zone, name, description, size, snapshot_id)
        self.attach_disk(instance_id, disk, device, delete_with_instance)

        return disk

    def reset_disk(self, disk_id, snapshot_id):
        """Reset a disk to its snapshot.

        Args:
            disk_id (str): Disk ID to reset.
            snapshot_id (str): ID of snapshot to reset the disk to.
        """
        self.get({
            'Action': 'ResetDisk',
            'DiskId': disk_id,
            'SnapshotId': snapshot_id
            })

    def delete_disk(self, disk_id):
        """Delete a disk from an instance.

        If the instance state is running, the disk will be removed after reboot.
        If the instance state is stopped, the disk will be removed immediately.

        Args:
            instance_id (str): ID of the instance to delete a disk from.
            disk_id (str): ID of the disk to delete.

        """

        self.get({
            'Action': 'DeleteDisk',
            'DiskId': disk_id
            })

    def create_instance(
            self, image_id, instance_type,
            security_group_id, instance_name=None,
            internet_max_bandwidth_in=None,
            internet_max_bandwidth_out=None,
            hostname=None, password=None, system_disk_type=None,
            internet_charge_type=None,
            instancechargetype='PrePaid', period=1,
            data_disks=None, description=None, zone_id=None):
        """Create an instance.

        Args:
            image_id (str): Which image id to use.
            instance_type (str): The type of the instance.
                To see options use describe_instance_types.
            security_group_id (str): The security group id to associate.
            instance_name (str): The name to use for the instance.
            internet_max_bandwidth_in (int): Max bandwidth in.
            internet_max_bandwidth_out (int): Max bandwidth out.
            hostname (str): The hostname to assign.
            password (str): The root password to assign.
            system_disk_type (str): cloud, ephemeral or ephemeral_hio.
                Default: cloud.
            internet_charge_type (str): PayByBandwidth or PayByTraffic.
                Default: PayByBandwidth.
            data_disks (list): List of *args or **kwargs to :class:`DiskMapping`
            description (str): A long description of the instance.
            zone_id (str): An Availability Zone in the region to put the instance in.
                E.g. 'cn-hangzhou-b'

        Returns:
            The id of the instance created.

        The data_disks argument is passed as *args (if not a dict) or **kwargs
        (if it is a dict) to create a new :class:`.model.DiskMapping`. To create
        two fully-specified data disks::

            [{
               'category': 'ephemeral',
               'size': 200,
               'name': 'mydiskname',
               'description': 'my disk description',
               'device': '/dev/xvdb'
            },
            {
               'category': 'ephemeral',
               'snapshot_id': 'snap-1234',
               'name': 'mydiskname',
               'description': 'my disk description',
               'device': '/dev/xvdb'
            }]

        To create two minimally-specified data disks of 2000GB each:::

            [('cloud', 2000), ('cloud', 2000)]

        The API supports up to 4 additional disks, each up to 2000GB, so to get
        the maximum disk space at instance creation, this should do the trick::

            [
                {'category': 'cloud', 'size': 2000},
                {'category': 'cloud', 'size': 2000},
                {'category': 'cloud', 'size': 2000},
                {'category': 'cloud', 'size': 2000}
            ]
        """
        if data_disks is None:
            data_disks = []
        params = {
            'Action': 'CreateInstance',
            'ImageId': image_id,
            'InstanceType': instance_type,
            'SecurityGroupId': security_group_id
        }
        if instance_name:
            params['InstanceName'] = instance_name
        if internet_max_bandwidth_in:
            params['InternetMaxBandwidthIn'] = str(internet_max_bandwidth_in)
        if internet_max_bandwidth_out:
            params['InternetMaxBandwidthOut'] = str(internet_max_bandwidth_out)
        if hostname:
            params['HostName'] = hostname
        if password:
            params['Password'] = password
        if system_disk_type:
            params['SystemDisk.Category'] = system_disk_type
        if internet_charge_type:
            params['InternetChargeType'] = internet_charge_type
        # Instance charge type & period
        if instancechargetype == 'PostPaid':
            params['InstanceChargeType'] = 'PostPaid'
        elif instancechargetype == 'PrePaid':
            params['InstanceChargeType'] = 'PrePaid'
            if not period or period not in [1,2,3,4,5,6,7,8,9,12,24,36]:
                exit("ERROR: PrePaid instances Must have a predefined period, in month [ 1-9, 12, 24, 36 ]")
            else:
                params['Period'] = period
        else:
            exit("InstanceChargeType is null. It is either PrePaid, or PostPaid")
        if data_disks:
            for i, disk in enumerate(data_disks):
                if isinstance(disk, dict):
                    ddisk = DiskMapping(**disk)
                else:
                    ddisk = DiskMapping(*disk)

                params.update(ddisk.api_dict(i+1))

        if description:
            params['Description'] = description
        if zone_id:
            params['ZoneId'] = zone_id

        return self.get(params)['InstanceId']

    def allocate_public_ip(self, instance_id):
        """Allocate and assign a public IP address to an instance.

        Args:
            instance_id (str): instance ID to add a public IP to.

        Returns:
            the public IP allocated to the instance.
        """
        return self.get({'Action': 'AllocatePublicIpAddress',
                         'InstanceId': instance_id})

    def create_and_start_instance(
            self, image_id, instance_type,
            initial_security_group_id, additional_security_group_ids=[],
            instance_name=None, internet_max_bandwidth_in=None,
            internet_max_bandwidth_out=None,
            hostname=None, password=None, system_disk_type=None,
            internet_charge_type=None,
            assign_public_ip=True, block_till_ready=True,
            data_disks=None, description=None, zone_id=None):
        """Create and start an instance.

        This is a convenience method that does more than just create_instance.
        You can specify a list of security groups (5 total) and the method also
        starts the instance. It can optionally block for the instance to be
        running - by default it does block.

        Specifying additional data disks is covered in :func:`create_instance`.

        Args:
            image_id (str): Which image id to use.
            instance_type (str): The type of the instance.
                To see options use describe_instance_types.
            initial_security_group_id (str): The security group id on creation.
            additional_security_group_ids (list): Additional security groups to
                use. Note: Max size 4.
            instance_name (str): The name to use for the instance.
            internet_max_bandwidth_in (int): Max bandwidth in.
            internet_max_bandwidth_out (int): Max bandwidth out.
            hostname (str): The hostname to assign.
            password (str): The root password to assign.
            system_disk_type (str): cloud, ephemeral or ephemeral_hio.
                Default: cloud.
            internet_charge_type (str): PayByBandwidth or PayByTraffic.
                Default: PayByBandwidth.
            assign_public_ip (bool): Whether the instance should get assigned
                a public ip address. Default: True.
            block_till_ready (bool): Whether to block till the instance is
                running. Default: True.
            data_disks (list): List of dictionaries defining additional data
                disk device mappings.
                Minimum example: [{'category': 'cloud', 'size': 1024}]
            description (str): A long description of the instance.
            zone_id (str): An Availability Zone in the region to put the instance in.
                E.g. 'cn-hangzhou-b'

        Returns:
            The id of the instance created.

        Raises:
            Error: if more then 4 additional security group ids specified.
            Error: if timeout while waiting for instance to be running.

        The data_disks device mapping dictionary describes the same Disk
        attributes as :func:`create_disk`::

            [{
               'category': 'ephemeral',
               'size': 200,
               'name': 'mydiskname',
               'description': 'my disk description',
               'device': '/dev/xvdb'
            },
            {
               'category': 'ephemeral',
               'snapshot_id': 'snap-1234',
               'name': 'mydiskname',
               'description': 'my disk description',
               'device': '/dev/xvdb'
            }]

        The API supports up to 4 additional disks, each up to 1TB, so to get the
        maximum disk space at instance creation, this should do the trick::

            [
                {'category': 'cloud', 'size': 1024},
                {'category': 'cloud', 'size': 1024},
                {'category': 'cloud', 'size': 1024},
                {'category': 'cloud', 'size': 1024}
            ]
        """
        if data_disks is None:
            data_disks = []
        # Cannot have more then 5 security groups total.
        if len(additional_security_group_ids) > 4:
            raise Error('Instance can have max 5 security groups')

        # Create the instance.
        logger.debug('creating instance')
        instance_id = self.create_instance(
            image_id, instance_type, initial_security_group_id,
            instance_name=instance_name,
            internet_max_bandwidth_in=internet_max_bandwidth_in,
            internet_max_bandwidth_out=internet_max_bandwidth_out,
            hostname=hostname, password=password,
            system_disk_type=system_disk_type,
            internet_charge_type=internet_charge_type,
            data_disks=data_disks, description=description, zone_id=zone_id)

        # Modify the security groups.
        if additional_security_group_ids:
            logger.debug('Adding additional security groups')
            time.sleep(10)
            for sg in additional_security_group_ids:
                self.join_security_group(instance_id, sg)

        # Assign public IP if specified.
        if assign_public_ip:
            self.allocate_public_ip(instance_id)

        # Start the instance.
        logger.debug('Starting the instance: %s', instance_id)
        time.sleep(10)
        self.start_instance(instance_id)

        # If specified block till the instance is running.
        if block_till_ready:
            running = False
            total_time = 0
            while total_time <= BLOCK_TILL_RUNNING_SECS:
                logger.debug('Waiting 30 secs for instance to be running')
                time.sleep(30)
                total_time += 30
                if self.get_instance(instance_id).status == 'Running':
                    running = True
                    break

            if not running:
                raise Error('Timed out while waiting for instance to run')

        return instance_id

    def describe_auto_snapshot_policy(self):
        '''Describe the Auto-Snapshot policy for both data- and system-disks.

        Returns:
            :class:`.model.AutoSnapshotPolicyResponse`.
        '''

        resp = self.get({'Action': 'DescribeAutoSnapshotPolicy'})
        exc_status = resp['AutoSnapshotExcutionStatus']
        sys_status = exc_status['SystemDiskExcutionStatus']
        data_status = exc_status['DataDiskExcutionStatus']
        status = AutoSnapshotExecutionStatus(sys_status, data_status)
        p = resp['AutoSnapshotPolicy']
        policy = AutoSnapshotPolicy(p['SystemDiskPolicyEnabled'] == 'true',
                                    int(p['SystemDiskPolicyTimePeriod']),
                                    int(p['SystemDiskPolicyRetentionDays']),
                                    p['SystemDiskPolicyRetentionLastWeek'] == 'true',
                                    p['DataDiskPolicyEnabled'] == 'true',
                                    int(p['DataDiskPolicyTimePeriod']),
                                    int(p['DataDiskPolicyRetentionDays']),
                                    p['DataDiskPolicyRetentionLastWeek'] == 'true')
        return AutoSnapshotPolicyStatus(status, policy)

    def modify_auto_snapshot_policy(self, system_disk_policy_enabled,
                                    system_disk_policy_time_period,
                                    system_disk_policy_retention_days,
                                    system_disk_policy_retention_last_week,
                                    data_disk_policy_enabled,
                                    data_disk_policy_time_period,
                                    data_disk_policy_retention_days,
                                    data_disk_policy_retention_last_week):
        '''Modify the account's auto-snapshot policy.

        Args:
            system_disk_policy_enabled (bool): Enable/Disable for system disks.
            system_disk_policy_time_period (int): Time period for system disk
                                                  auto snapshots.
            system_disk_policy_retention_days (int): Number of days to retain.
            system_disk_policy_retention_last_week (bool): Keep/Discard Sunday's
                                                           auto-snapshot.
            data_disk_policy_enabled (bool): Enable/Disable for data disks.
            data_disk_policy_time_period (int): Time period for data disk auto
                                                snapshots.
            data_disk_policy_retention_days (int): Number of days to retain.
            data_disk_policy_retention_last_week (bool): Keep/Discard Sunday's
                                                           auto-snapshot.
        '''

        self.get({
            'Action': 'ModifyAutoSnapshotPolicy',
            'SystemDiskPolicyEnabled': str(system_disk_policy_enabled).lower(),
            'SystemDiskPolicyTimePeriod': system_disk_policy_time_period,
            'SystemDiskPolicyRetentionDays': system_disk_policy_retention_days,
            'SystemDiskPolicyRetentionLastWeek': str(system_disk_policy_retention_last_week).lower(),
            'DataDiskPolicyEnabled': str(data_disk_policy_enabled).lower(),
            'DataDiskPolicyTimePeriod': data_disk_policy_time_period,
            'DataDiskPolicyRetentionDays': data_disk_policy_retention_days,
            'DataDiskPolicyRetentionLastWeek': str(data_disk_policy_retention_last_week).lower()
            })

    def describe_disks(self, zone_id=None, disk_ids=None, instance_id=None,
                       disk_type=None, category=None, status=None,
                       snapshot_id=None,portable=None,
                       delete_with_instance=None, delete_auto_snapshot=None):
        """List the disks in the region. All arguments are optional to allow
        restricting the disks retrieved.

        Args:
            zone_id (str): Availability Zone of the disks.
            disk_ids (list): List of disk ids to retrieve.
            instance_id (str): ID of instance retrieved disks are attached to.
            disk_type (str): "system", "data", or "all" (default).
            category (str): "cloud", "ephemeral", or "all" (default).
            status (str): Restrict to disks only with this status.
                          "In_use", "Available", "Attaching", "Detaching",
                          "Creating", "ReIniting", or "All" (default).
            snapshot_id (str): Snapshot used to create the disk.
            portable (bool): Whether the disk can be detached and re-attached
                             elsewhere.
            delete_with_instance (bool): Whether the disk will be deleted with
                                         its associated instance.
            delete_auto_snapshot (bool): Whether the AutoSnapshotPolicy will be
                                         deleted with the Disk.

        Returns:
            List of :class:`.model.Disk` objects.
        """
        disks = []
        params = {'Action': 'DescribeDisks'}
        if zone_id:
            params['ZoneId'] = zone_id
        if disk_ids:
            params['DiskIds'] = ','.join(disk_ids)
        if instance_id:
            params['InstanceId'] = instance_id

        for resp in self.get(params, paginated=True):
            for disk in resp['Disks']['Disk']:
                disks.append(Disk(disk['DiskId'],
                                  disk['Type'],
                                  disk['Category'],
                                  disk['Size'],
                                  dateutil.parser.parse(disk['AttachedTime']) if disk['AttachedTime'] != '' else None,
                                  dateutil.parser.parse(disk['CreationTime']) if disk['CreationTime'] != '' else None,
                                  disk['DeleteAutoSnapshot'] == 'true' if disk['DeleteAutoSnapshot'] != '' else None,
                                  disk['DeleteWithInstance'] == 'true' if disk['DeleteWithInstance'] != '' else None,
                                  disk['Description'] if disk['Description'] != '' else None,
                                  dateutil.parser.parse(disk['DetachedTime']) if disk['DetachedTime'] != '' else None,
                                  disk['Device'] if disk['Device'] != '' else None,
                                  disk['ImageId'] if disk['ImageId'] != '' else None,
                                  disk['InstanceId'] if disk['InstanceId'] != '' else None,
                                  disk['OperationLocks']['OperationLock'],
                                  disk['Portable'] == 'true' if disk['Portable'] != '' else None,
                                  disk['ProductCode'] if disk['ProductCode'] != '' else None,
                                  disk['SourceSnapshotId'] if disk['SourceSnapshotId'] != '' else None,
                                  disk['Status'] if disk['Status'] != '' else None,
                                  disk['ZoneId'] if disk['ZoneId'] != '' else None))
        return disks

    def describe_instance_types(self):
        """List the instance types available.

        Returns:
            List of :class:`.model.InstanceType`.
        """
        instance_types = []
        resp = self.get({'Action': 'DescribeInstanceTypes'})
        for instance_type in resp['InstanceTypes']['InstanceType']:
            instance_types.append(
                InstanceType(instance_type['InstanceTypeId'],
                             int(instance_type['CpuCoreCount']),
                             int(instance_type['MemorySize'])))

        return instance_types

    def describe_instance_disks(self, instance_id):
        """List the disks associated with an instance.
        This is now only a helper method which calls describe_disks with an ID.

        Args:
            instance_id (str): The id of the instance.

        Returns:
            List of :class:`.model.Disk`.
        """
        return self.describe_disks(instance_id=instance_id)

    def modify_disk(self, disk_id, name=None, description=None,
                    delete_with_instance=None):
        """Modify information about a disk.

        Args:
            disk_id (str): The Disk to modify/update.
            name (str): The new disk name.
            description (str): The new disk description.
            delete_with_instance (str): Change whether to delete the disk with
                                        its associated instance.

        """
        params = {'Action': 'ModifyDiskAttribute',
                  'DiskId': disk_id}
        if name is not None:
            params['DiskName'] = name
        if description is not None:
            params['Description'] = description
        if delete_with_instance is not None:
            params['DeleteWithInstance'] = delete_with_instance

        self.get(params)

    def reinit_disk(self, disk_id):
        """Re-initialize a disk to it's original Image.

        Args:
            disk_id (str): ID of the Disk to re-initialize.
        """
        self.get({'Action': 'ReInitDisk', 'DiskId': disk_id})

    def delete_snapshot(self, instance_id, snapshot_id):
        """Delete a snapshot.

        Args:
            instance_id (str): The id of the instance.
            snapshot_id (str): The id of the snapshot.
        """
        self.get({'Action': 'DeleteSnapshot',
                  'InstanceId': instance_id,
                  'SnapshotId': snapshot_id})

    def describe_snapshot(self, snapshot_id):
        """Describe a snapshot.

        Args:
            snapshot_id (str): The id of the snapshot.

        Returns:
            :class:`.model.Snapshot`.
        """
        snaps = self.describe_snapshots(snapshot_ids=[snapshot_id])
        if len(snaps) == 1:
            return snaps[0]
        else:
            raise Error("Could not find the snapshot: %s" % snapshot_id)

    def describe_snapshots(self, instance_id=None, disk_id=None,
                           snapshot_ids=None):
        '''Describe snapshots, filtering by ids or originating disk.

        Args:
            instance_id (str): Instance ID.
            disk_id (str): The originating disk ID to get snapshots for.
            snapshot_ids (list): Filter to up to 10 specific snapshot IDs

        Returns:
            A list of :class:`.model.Snapshot`.
        '''

        snapshots = []
        params = {'Action': 'DescribeSnapshots'}
        if instance_id:
            params['InstanceId'] = instance_id
        if disk_id:
            params['DiskId'] = disk_id
        if snapshot_ids:
            params['SnapshotIds'] = json.dumps(snapshot_ids)

        for resp in self.get(params, paginated=True):
            for snapshot in resp['Snapshots']['Snapshot']:
                snapshots.append(Snapshot(
                    snapshot['SnapshotId'],
                    snapshot.get('SnapshotName', None),
                    int(snapshot['Progress'][:-1]),
                    dateutil.parser.parse(snapshot['CreationTime']),
                    snapshot.get('Description', None),
                    snapshot.get('SourceDiskId', None),
                    snapshot.get('SourceDiskType', None),
                    int(snapshot.get('SourceDiskSize', None))))

        return snapshots

    def create_snapshot(self, instance_id, disk_id, snapshot_name=None,
                        timeout_secs=None, description=None):
        """Create a snapshot of a disk.

        The instance has to be in the running or stopped state.

        Args:
            instance_id (str): The id of the instance.
            disk_id (str): The id of the disk.
            snapshot_name (str): The name to assign to the snapshot.
            timeout_secs (int): If you want to block till the snapshot
                is ready you can specify how long to wait for.
            description (str): A description of the snapshot.

        Returns:
            The snapshot id.

        Raises:
            Error: if a timeout is given and the snapshot is not ready by then.
        """
        params = {
            'Action': 'CreateSnapshot',
            'InstanceId': instance_id,
            'DiskId': disk_id,
        }
        if snapshot_name:
            params['SnapshotName'] = snapshot_name

        if description:
            params['Description'] = description

        # Create the snapshot.
        snapshot_id = self.get(params)['SnapshotId']

        # If specified block till the snapshot is ready.
        if timeout_secs:
            total_time = 0
            created = False
            while total_time <= timeout_secs:
                logger.debug('Waiting 30 secs for snapshot')
                time.sleep(30)
                total_time += 30
                snapshot = self.describe_snapshot(snapshot_id)
                if snapshot.progress == 100:
                    created = True
                    break

        # If the snapshot wasn't ready in the specified time error out.
        if timeout_secs and not created:
            raise Error('Snapshot %s not ready in %s seconds' % (
                snapshot_id, timeout_secs))

        return snapshot_id

    def describe_images(self, image_ids=None, owner_alias=None, snapshot_id=None):
        """List images in the region matching params.

        Args:
            image_ids (list): List of image ids to filter on.
            owner_alias (list): List of owner alias to filter on. Can be
                values: system, self, others or marketplace.
            snapshot_id (str): List images only based off of this snapshot.

        Returns:
            List of :class`.model.Image` objects.
        """
        if image_ids is None:
            image_ids = []
        if owner_alias is None:
            owner_alias = []

        images = []

        params = {'Action': 'DescribeImages'}
        if image_ids:
            params['ImageId'] = ','.join(image_ids)
        if owner_alias:
            params['ImageOwnerAlias'] = '+'.join(owner_alias)
        if snapshot_id:
            params['SnapshotId'] = snapshot_id

        for resp in self.get(params, paginated=True):
            for item in resp['Images']['Image']:
                images.append(Image(
                    item['ImageId'],
                    item['ImageVersion'] if 'ImageVersion' in item else None,
                    item['ImageName'],
                    item['Description'] if 'Description' in item else None,
                    int(item['Size']) if 'Size' in item else None,
                    item['Architecture'] if 'Architecture' in item else None,
                    item['ImageOwnerAlias'],
                    item['OSName'] if 'OSName' in item else None))

        return images

    def delete_image(self, image_id):
        """Delete an image.

        Args:
            image_id (str): The id of the image.
        """
        self.get({'Action': 'DeleteImage',
                  'ImageId': image_id})

    def create_image(self, snapshot_id, image_version=None,
                     description=None, os_name=None):
        """Create an image.

        Args:
            snapshot_id (str): The id of the snapshot to create the image from.
            image_version (str): The version of the image.
            description (str): The description of the image.
            os_name (str): The os name.

        Returns:
            The image id.
        """
        params = {
            'Action': 'CreateImage',
            'SnapshotId': snapshot_id
        }
        if image_version:
            params['ImageVersion'] = image_version
        if description:
            params['Description'] = description
        if os_name:
            params['OSName'] = os_name

        return self.get(params)['ImageId']

    def create_image_from_instance(
            self, instance_id, image_version=None, description=None,
            os_name=None, timeout_secs=600):
        """Create an image from an instance.

        This is a convenience method that handles creating the snapshot
        from the system disk and then creates the image.

        Args:
            instance_id (str): The id of the instance.
            image_version (str): The version of the image.
            description (str): The description.
            os_name (str): The os name.
            timeout_secs (int): How long to wait for the snapshot to be
                created. Default: 600.

        Returns:
            The (snapshot id, image id) pair.

        Raises:
            Error: if the system disk cannot be found or if the snapshot
                creation process times out.
        """
        # Get the system disk id.
        logger.debug('Getting system disk for %s', instance_id)
        disks = self.describe_instance_disks(instance_id)
        system_disk = next((d for d in disks if d.disk_type == 'system'), None)
        if not system_disk:
            raise Error('System disk for %s not found' % instance_id)

        # Create the snapshot.
        logger.debug(
            'Creating snapshot for system disk %s' %
            system_disk.disk_id)
        snapshot_id = self.create_snapshot(instance_id, system_disk.disk_id,
                                           timeout_secs=timeout_secs)

        # Create the image.
        logger.debug('Creating image from snapshot %s', snapshot_id)
        image_id = self.create_image(snapshot_id,
                                     image_version=image_version,
                                     description=description, os_name=os_name)
        time.sleep(30)

        return (snapshot_id, image_id)

    def describe_security_groups(self):
        """List all the security groups in the region.

        Returns:
            List of :class:`.model.SecurityGroupInfo`.
        """
        infos = []
        for resp in self.get({'Action': 'DescribeSecurityGroups'},
                             paginated=True):
            for item in resp['SecurityGroups']['SecurityGroup']:
                infos.append(SecurityGroupInfo(
                    item['SecurityGroupId'],
                    item['Description'] if 'Description' in item else None))

        return infos

    def get_security_group_ids(self):
        """List all the security group ids in the region.

        Returns:
            List of security group ids.
        """
        return [x.security_group_id for x in self.describe_security_groups()]

    def create_security_group(self, description):
        """Create a security group.

        Args:
            description (str): The description.

        Returns:
            The security group id.
        """
        return self.get({'Action': 'CreateSecurityGroup',
                         'Description': description})['SecurityGroupId']

    def get_security_group(self, security_group_id):
        """Get a security group.

        Args:
            security_group_id (str): The id of the security group.

        Returns:
            The :class:`.model.SecurityGroup` object.
        """
        outside_resp = self.get({'Action': 'DescribeSecurityGroupAttribute',
                                 'SecurityGroupId': security_group_id,
                                 'NicType': 'internet'})
        inside_resp = self.get({'Action': 'DescribeSecurityGroupAttribute',
                                'SecurityGroupId': security_group_id,
                                'NicType': 'intranet'})
        permissions = []
        for p in outside_resp['Permissions']['Permission']:
            permissions.append(SecurityGroupPermission(
                p['IpProtocol'],
                p['PortRange'],
                p['SourceCidrIp'] if 'SourceCidrIp' in p else None,
                p['SourceGroupId'] if 'SourceGroupId' in p else None,
                p['Policy'],
                p['NicType']))
        for p in inside_resp['Permissions']['Permission']:
            permissions.append(SecurityGroupPermission(
                p['IpProtocol'],
                p['PortRange'],
                p['SourceCidrIp'] if 'SourceCidrIp' in p else None,
                p['SourceGroupId'] if 'SourceGroupId' in p else None,
                p['Policy'],
                p['NicType']))

        return SecurityGroup(outside_resp['RegionId'],
                             outside_resp['SecurityGroupId'],
                             outside_resp['Description'],
                             permissions)

    def delete_security_group(self, security_group_id):
        """Delete a security group.

        Args:
            security_group_id (str): The id of the security group.
        """
        self.get({'Action': 'DeleteSecurityGroup',
                  'SecurityGroupId': security_group_id})

    def add_external_cidr_ip_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip, policy=None):
        """Add a rule for an external CidrIp to a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._add_security_rule(security_group_id, ip_protocol,
                                port_range, source_cidr_ip=source_cidr_ip,
                                policy=policy, nic_type='internet')

    def add_internal_cidr_ip_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip, policy=None):
        """Add a rule for an internal CidrIp to a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._add_security_rule(security_group_id, ip_protocol,
                                port_range, source_cidr_ip=source_cidr_ip,
                                policy=policy, nic_type='intranet')

    def add_group_rule(
            self, security_group_id, ip_protocol, port_range,
            source_group_id, policy=None):
        """Add a rule for one security group to access another security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_group_id (str): Source security group.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._add_security_rule(security_group_id, ip_protocol,
                                port_range, source_group_id=source_group_id,
                                policy=policy, nic_type='intranet')

    def _add_security_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip=None, source_group_id=None, policy=None,
            nic_type=None):
        """Add a rule to a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            source_group_id (str): Source security group.
            policy (str): Accept, Drop or Reject. Default: Accept.
            nic_type (str): internet or intranet. Default: internet.
        """
        params = {
            'Action': 'AuthorizeSecurityGroup',
            'SecurityGroupId': security_group_id,
            'IpProtocol': ip_protocol,
            'PortRange': port_range
        }
        if source_cidr_ip:
            params['SourceCidrIp'] = source_cidr_ip
        if source_group_id:
            params['SourceGroupId'] = source_group_id
        if policy:
            params['Policy'] = policy
        if nic_type:
            params['NicType'] = nic_type

        self.get(params)

    def remove_external_cidr_ip_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip, policy=None):
        """Remove a rule for an external CidrIp from a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._remove_security_rule(security_group_id, ip_protocol,
                                   port_range, source_cidr_ip=source_cidr_ip,
                                   policy=policy, nic_type='internet')

    def remove_internal_cidr_ip_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip, policy=None):
        """Remove a rule for an internal CidrIp from a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._remove_security_rule(security_group_id, ip_protocol,
                                   port_range, source_cidr_ip=source_cidr_ip,
                                   policy=policy, nic_type='intranet')

    def remove_group_rule(
            self, security_group_id, ip_protocol, port_range,
            source_group_id, policy=None):
        """Remove a rule for a security group to access another security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_group_id (str): Source security group.
            policy (str): Accept, Drop or Reject. Default: Accept.
        """
        self._remove_security_rule(security_group_id, ip_protocol,
                                   port_range, source_group_id=source_group_id,
                                   policy=policy, nic_type='intranet')

    def _remove_security_rule(
            self, security_group_id, ip_protocol, port_range,
            source_cidr_ip=None, source_group_id=None, policy=None,
            nic_type=None):
        """Remove a rule from a security group.

        Args:
            security_group_id (str): The id of the security group.
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            source_group_id (str): Source security group.
            policy (str): Accept, Drop or Reject. Default: Accept.
            nic_type (str): internet or intranet. Default: internet.
        """
        params = {
            'Action': 'RevokeSecurityGroup',
            'SecurityGroupId': security_group_id,
            'IpProtocol': ip_protocol,
            'PortRange': port_range
        }
        if source_cidr_ip:
            params['SourceCidrIp'] = source_cidr_ip
        if source_group_id:
            params['SourceGroupId'] = source_group_id
        if policy:
            params['Policy'] = policy
        if nic_type:
            params['NicType'] = nic_type

        self.get(params)
