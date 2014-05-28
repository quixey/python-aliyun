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

from aliyun.connection import Connection
from aliyun.ecs.model import (
    Disk,
    Image,
    Instance,
    InstanceStatus,
    InstanceType,
    Region,
    SecurityGroup,
    SecurityGroupInfo,
    SecurityGroupPermission,
    Snapshot
)
import dateutil.parser
import logging
import time


BLOCK_TILL_RUNNING_SECS = 600


class Error(Exception):

    """Base exception class for this module."""


class EcsConnection(Connection):

    """A connection to Aliyun ECS service."""

    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        """Construct a connection to the ECS service.

        Args:
            region_id (str): The id of the region to connect to.
            access_key_id (str): The access key id.
            secret_access_key (str): The secret access key.
        """
        super(EcsConnection, self).__init__(
            region_id, 'ecs', access_key_id=access_key_id,
            secret_access_key=secret_access_key)

    def get_all_regions(self):
        """Get all regions.

        Returns:
            List of Region.
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

    def get_all_instance_status(self):
        """Get the instance statuses.
        
        Returns:
            The list of InstanceStatus.
        """
        instance_status = []
        params = {
            'Action': 'DescribeInstanceStatus'
        }
    
        for resp in self.get(params, paginated=True):
            for item in resp['InstanceStatuses']['InstanceStatus']:
                instance_status.append(
                    InstanceStatus(item['InstanceId'], item['Status']))
        return instance_status

    def get_all_instance_ids(self):
        """Get all the instance ids in a region.

        Returns:
            The list of instance ids.
        """
        return [x.instance_id for x in self.get_all_instance_status()]

    def get_instance(self, instance_id):
        """Get an instance.

        Args:
            instance_id (str): The id of the instance.

        Returns:
            The Instance if found.

        Raises:
            Error if not found.
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
            dateutil.parser.parse(resp['CreationTime']))

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
                        new_security_group_id=None):
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

        self.get(params)

    def modify_instance_spec(self, instance_id, instance_type=None,
            internet_max_bandwidth_out=None, internet_max_bandwidth_in=None):
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

    def add_disk(self, instance_id, size=None, snapshot_id=None):
        """Create and attach a non-durable disk to an instance.
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

        Returns:
            disk_id (str): the ID to reference the created disk.

        Raises:
            Error if size and snapshot_id are used.
            Error InvalidSnapshot.TooOld if referenced snapshot is too old.

        """

        if size is not None and snapshot_id is not None:
            raise Error("Use size or snapshot_id. Not both.")

        params = {
                'Action': 'AddDisk',
                'InstanceId': instance_id
            }

        if size is not None:
            params['Size'] = size

        if snapshot_id is not None:
            params['SnapshotId'] = snapshot_id

        return self.get(params)

    def delete_disk(self, instance_id, disk_id):
        """Delete a disk from an instance.

        If the instance state is running, the disk will be removed after reboot.
        If the instance state is stopped, the disk will be removed immediately.

        Args:
            instance_id (str): ID of the instance to delete a disk from.
            disk_id (str): ID of the disk to delete.

        """

        self.get({
                'Action': 'DeleteDisk',
                'InstanceId': instance_id,
                'DiskId': disk_id
                })

    def create_instance(
            self, image_id, instance_type,
            security_group_id, instance_name=None,
            internet_max_bandwidth_in=None,
            internet_max_bandwidth_out=None,
            hostname=None, password=None, system_disk_type=None,
            internet_charge_type=None,
            data_disks=[]):
        """Create an instance.

        Currently specifying additional data disks is not supported.
        Future updates will add this feature.

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
            data_disks (list): Two-tuples of (category, size or Snapshot ID).
                E.g. [('ephemeral', 200), ('cloud', 'snap-14i1oh')]

        Returns:
            The id of the instance created.
        """
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
        if data_disks != []:
            for i, disk in enumerate(data_disks):
                params['DataDisk.%s.Category' % str(i+1)] = disk[0]
                if isinstance(disk[1], int):
                    params['DataDisk.%s.Size' % str(i+1)] = disk[1]
                else:
                    params['DataDisk.%s.SnapshotId' % str(i+1)] = disk[1]

        return self.get(params)['InstanceId']

    def allocate_public_ip(self, instance_id):
        """Allocate and assign a public IP address to an instance.

        Args:
            instance_id (str): instance ID to add a public IP to.

        Returns:
            IpAddress: the public IP allocated to the instance.
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
            data_disks=[]):
        """Create and start an instance.

        This is a convenience method that does more than just create_instance.
        You can specify a list of security groups (5 total) and the method also
        starts the instance. It can optionally block for the instance to be
        running - by default it does block.

        Currently specifying additional data disks is not supported.
        Future updates will add this feature.

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
            data_disks (list): Two-tuples of (category, size or Snapshot ID).
                E.g. [('ephemeral', 200), ('cloud', 'snap-14i1oh')]

        Returns:
            The id of the instance created.

        Raises:
            Error if more then 4 additional security group ids specified.
            Error if timeout while waiting for instance to be running.
        """
        # Cannot have more then 5 security groups total.
        if len(additional_security_group_ids) > 4:
            raise Error('Instance can have max 5 security groups')

        # Create the instance.
        self.logging.debug('creating instance')
        instance_id = self.create_instance(
            image_id, instance_type, initial_security_group_id,
            instance_name=instance_name,
            internet_max_bandwidth_in=internet_max_bandwidth_in,
            internet_max_bandwidth_out=internet_max_bandwidth_out,
            hostname=hostname, password=password,
            system_disk_type=system_disk_type,
            internet_charge_type=internet_charge_type,
            data_disks=data_disks)

        # Modify the security groups.
        if additional_security_group_ids:
            self.logging.debug('Adding additional security groups')
            time.sleep(10)
            for sg in additional_security_group_ids:
                self.join_security_group(instance_id, sg)

        # Assign public IP if specified.
        if assign_public_ip:
            self.allocate_public_ip(instance_id)

        # Start the instance.
        self.logging.debug('Starting the instance: %s' % instance_id)
        time.sleep(10)
        self.start_instance(instance_id)

        # If specified block till the instance is running.
        if block_till_ready:
            running = False
            total_time = 0
            while total_time <= BLOCK_TILL_RUNNING_SECS:
                self.logging.debug('Waiting 30 secs for instance to be running')
                time.sleep(30)
                total_time += 30
                if self.get_instance(instance_id).status == 'Running':
                    running = True
                    break

            if not running:
                raise Error('Timed out while waiting for instance to run')

        return instance_id

    def describe_instance_types(self):
        """List the instance types available.

        Returns:
            List of InstanceType.
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

        Args:
            instance_id (str): The id of the instance.

        Returns:
            List of Disk.
        """
        disks = []
        resp = self.get({'Action': 'DescribeInstanceDisks',
                         'InstanceId': instance_id})
        for disk in resp['Disks']['Disk']:
            disks.append(Disk(disk['DiskId'], disk['Type'],
                              disk['Category'], int(disk['Size'])))

        return disks

    def delete_snapshot(self, instance_id, disk_id, snapshot_id):
        """Delete a snapshot.

        Args:
            instance_id (str): The id of the instance.
            disk_id (str): The id of the disk.
            snapshot_id (str): The id of the snapshot.
        """
        self.get({'Action': 'DeleteSnapshot',
                  'InstanceId': instance_id,
                  'DiskId': disk_id,
                  'SnapshotId': snapshot_id})

    def describe_snapshot(self, snapshot_id):
        """Describe a snapshot.

        Args:
            snapshot_id (str): The id of the snapshot.

        Returns:
            A Snapshot.
        """
        resp = self.get({'Action': 'DescribeSnapshotAttribute',
                         'SnapshotId': snapshot_id})
        return Snapshot(
            resp['SnapshotId'],
            resp['SnapshotName'] if 'SnapshotName' in resp else None,
            int(resp['Progress']),
            dateutil.parser.parse(resp['CreationTime']))

    def describe_snapshots(self, instance_id, disk_id):
        """Describe snapshots for a given disk.

        Args:
            instance_id (str): The id of the instance.
            disk_id (str): The id of the disk.

        Returns:
            A list of Snapshot.
        """
        snapshots = []
        resp = self.get({'Action': 'DescribeSnapshots',
                         'InstanceId': instance_id,
                         'DiskId': disk_id})
        for snapshot in resp['Snapshots']['Snapshot']:
            snapshots.append(Snapshot(
                snapshot['SnapshotId'],
                snapshot[
                    'SnapshotName'] if 'SnapshotName' in snapshot else None,
                int(snapshot['Progress']),
                dateutil.parser.parse(snapshot['CreationTime'])))

        return snapshots

    def create_snapshot(self, instance_id, disk_id, snapshot_name=None,
                        timeout_secs=None):
        """Create a snapshot of a disk.

        The instance has to be in the running or stopped state.

        Args:
            instance_id (str): The id of the instance.
            disk_id (str): The id of the disk.
            snapshot_name (str): The name to assign to the snapshot.
            timeout_secs (int): If you want to block till the snapshot
                is ready you can specify how long to wait for.

        Returns:
            The snapshot id.

        Raises:
            Error if a timeout is given and the snapshot is not ready by then.
        """
        params = {
            'Action': 'CreateSnapshot',
            'InstanceId': instance_id,
            'DiskId': disk_id
        }
        if snapshot_name:
            params['SnapshotName'] = snapshot_name

        # Create the snapshot.
        snapshot_id = self.get(params)['SnapshotId']

        # If specified block till the snapshot is ready.
        if timeout_secs:
            total_time = 0
            created = False
            while total_time <= timeout_secs:
                self.logging.debug('Waiting 30 secs for snapshot')
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

    def describe_images(self, image_ids=[], owner_alias=[]):
        """List images in the region matching params.

        Args:
            image_ids (list): List of image ids to filter on.
            owner_alias (list): List of owner alias to filter on. Can be
                values: system, self or others.

        Returns:
            List of Image.
        """
        images = []

        params = {'Action': 'DescribeImages'}
        if image_ids:
            params['ImageId'] = ','.join(image_ids)
        if owner_alias:
            params['ImageOwnerAlias'] = ','.join(owner_alias)

        for resp in self.get(params, paginated=True):
            for item in resp['Images']['Image']:
                images.append(Image(
                    item['ImageId'],
                    item['ImageVersion'] if 'ImageVersion' in item else None,
                    item['Platform'],
                    item['Description'] if 'Description' in item else None,
                    int(item['Size']) if 'Size' in item else None,
                    item['Architecture'] if 'Architecture' in item else None,
                    item['ImageOwnerAlias'],
                    item['OSName'] if 'OSName' in item else None,
                    item['Visibility'] if 'Visibility' in item else None))

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
            Error if the system disk cannot be found or if the snapshot
                creation process times out.
        """
        # Get the system disk id.
        self.logging.debug('Getting system disk for %s' % instance_id)
        disks = self.describe_instance_disks(instance_id)
        system_disk = next((d for d in disks if d.disk_type == 'system'), None)
        if not system_disk:
            raise Error('System disk for %s not found' % instance_id)

        # Create the snapshot.
        self.logging.debug(
            'Creating snapshot for system disk %s' %
            system_disk.disk_id)
        snapshot_id = self.create_snapshot(instance_id, system_disk.disk_id,
                                           timeout_secs=timeout_secs)

        # Create the image.
        self.logging.debug('Creating image from snapshot %s' % snapshot_id)
        image_id = self.create_image(snapshot_id,
                                     image_version=image_version,
                                     description=description, os_name=os_name)
        time.sleep(30)

        return (snapshot_id, image_id)

    def describe_security_groups(self):
        """List all the security groups in the region.

        Returns:
            List of SecurityGroupInfo.
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
            The SecurityGroup.
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