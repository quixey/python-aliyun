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

    def __init__(self, region_id, local_name):
        """Constructor.

        Args:
            region_id (str): The id of the region.
            local_name (str): The local name of the region.
        """
        self.region_id = region_id
        self.local_name = local_name

    def __repr__(self):
        return u'<Region %s (%s) at %s>' % (
            self.region_id, self.local_name, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class Instance(object):

    """An Aliyun ECS instance."""

    def __init__(
            self, instance_id, name, image_id, region_id, instance_type,
            hostname, status, security_group_ids, public_ip_addresses,
            internal_ip_addresses, internet_charge_type,
            internet_max_bandwidth_in, internet_max_bandwidth_out,
            creation_time, description, cluster_id, operation_locks, zone_id):
        """"Constructor.

        Args:
            instance_id (str): The id of the instance.
            name (str): The name of the instance.
            image_id (str): The id of the image used to create the instance.
            region_id (str): The id of the region in which the instance lies.
            instance_type (str): The type of the instance.
            hostname (str): The hostname of the instance.
            status (str): The status of the instance.
            security_group_ids (list): The security group ids for the instance.
            public_ip_addresses (list): Its public ip addresses.
            internal_ip_addresses (list): Its internal ip addresses.
            internet_charge_type (str): The accounting method of network use.
            internet_max_bandwidth_in (int): The max incoming bandwidth.
            internet_max_bandwidth_out (int): The max outgoing bandwidth.
            creation_time (datetime): Its creation time.
            description (str): A long description of the instance.
            operation_locks (list of str): Any held operation locks. 'security'
                                           and/or 'financial'
            zone_id (str): The ID of the Availability Zone this instance is in.
        """
        self.instance_id = instance_id
        self.name = name
        self.image_id = image_id
        self.region_id = region_id
        self.instance_type = instance_type
        self.hostname = hostname
        self.status = status
        self.security_group_ids = security_group_ids
        self.public_ip_addresses = public_ip_addresses
        self.internal_ip_addresses = internal_ip_addresses
        self.internet_charge_type = internet_charge_type
        self.internet_max_bandwidth_in = internet_max_bandwidth_in
        self.internet_max_bandwidth_out = internet_max_bandwidth_out
        self.creation_time = creation_time
        self.description = description
        self.operation_locks = operation_locks
        self.zone_id = zone_id

    def __repr__(self):
        return '<Instance %s at %s>' % (self.instance_id, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class InstanceStatus(object):

    def __init__(self, instance_id, status):
        """Constructor.

        Args:
            instance_id (str): The id of the instance.
            status (str): The status of the instance.
        """
        self.instance_id = instance_id
        self.status = status

    def __repr__(self):
        return u'<InstanceId %s is %s at %s>' % (
            self.instance_id, self.status, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class InstanceType(object):

    def __init__(self, instance_type_id, cpu_core_count, memory_size):
        """Constructor.

        Args:
            instance_type_id (str): The instance type id.
            cpu_core_count (int): The number of cpus.
            memory_size (int): The memory size in GB.
        """
        self.instance_type_id = instance_type_id
        self.cpu_core_count = cpu_core_count
        self.memory_size = memory_size

    def __repr__(self):
        return u'<InstanceType %s has %s cores and %sGB memory at %s>' % (
            self.instance_type_id, self.cpu_core_count, self.memory_size,
            id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class Snapshot(object):

    def __init__(self, snapshot_id, snapshot_name, progress, creation_time,
                 description=None, source_disk_id=None, source_disk_type=None,
                 source_disk_size=None):
        """Snapshot for ECS Disk.

        snapshot_id (str): The id of the snapshot.
        snapshot_name (str): The name of the snapshot.
        progress (int): The progress ready percentage.
        creation_time (datetime): Its creation time.
        source_disk_id (str): ID of the original disk.
        source_disk_type (str): "data" or "system", for the original disk.
        source_disk_size (int): size of the original disk in GB.
        """
        self.snapshot_id = snapshot_id
        self.snapshot_name = snapshot_name
        self.progress = progress
        self.creation_time = creation_time
        self.source_disk_id = source_disk_id
        self.source_disk_type = source_disk_type
        self.source_disk_size = source_disk_size

    def __repr__(self):
        return u'<Snapshot %s is %s%% ready at %s>' % (
            self.snapshot_id, self.progress, id(self))

    def __eq__(self, other):
        print self.__dict__
        print other.__dict__
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class AutoSnapshotPolicy(object):

    def __init__(self, system_disk_enabled, system_disk_time_period,
                 system_disk_retention_days, system_disk_retention_last_week,
                 data_disk_enabled, data_disk_time_period,
                 data_disk_retention_days, data_disk_retention_last_week):
        '''AutoSnapshotPolicy describing how to manage snapshot rotation.

        The policy is composed of a system- and data-disk policy, but the API
        does not handle them independently, so this object combines them too.

        Arguments:
            system_disk_enabled (bool): wether the policy is on for SystemDisk
            system_disk_time_period (int): the time period during which to
                                           auto-snapshot. There are 4 choices:
                                           1, 2, 3 or 4. These correspond to
                                           these time periods:
                                           1: 1:00 - 7:00
                                           2: 7:00 - 13:00
                                           3: 13:00 - 19:00
                                           4: 19:00 - 1:00
                                           All times Beijing Time.
            system_disk_retention_days (int): number of days to retain.
                                              must be between 1 and 3, inclusive
            system_disk_retention_last_week (bool): wether to retain a weekly
                                                    snapshot from Sundays.
            data_disk_enabled (bool): wether the policy is on for DataDisk
            data_disk_time_period (int): the time period during which to
                                         auto-snapshot. There are 4 choices: 1,
                                         2, 3 or 4. These correspond to these
                                         time periods:
                                         1: 1:00 - 7:00
                                         2: 7:00 - 13:00
                                         3: 13:00 - 19:00
                                         4: 19:00 - 1:00
                                         All times Beijing Time.
            data_disk_retention_days (int): number of days to retain.
                                              must be between 1 and 3, inclusive
            data_disk_retention_last_week (bool): wether to retain a weekly
                                                    snapshot from Sundays.
        '''
        self.system_disk_enabled = system_disk_enabled
        self.system_disk_time_period = system_disk_time_period
        self.system_disk_retention_days = system_disk_retention_days
        self.system_disk_retention_last_week = system_disk_retention_last_week
        self.data_disk_enabled = data_disk_enabled
        self.data_disk_time_period = data_disk_time_period
        self.data_disk_retention_days = data_disk_retention_days
        self.data_disk_retention_last_week = data_disk_retention_last_week

    def __repr__(self):
        return u'<AutoSnapshotPolicy at %s>' % id(self)

    def __eq__(self, other):
        print self.__dict__
        print other.__dict__
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class AutoSnapshotExecutionStatus(object):

    def __init__(self, system_disk_execution_status, data_disk_execution_status):
        '''Description of the status of the auto-snapshot policy's executions.

        The arguments are either 'Standby', 'Executed', or 'Failed'.
            Standby: The policy is created, but disabled.
            Executed: The latest auto-snapshot was successful.
            Failed: The latest auto-snapshot was unsuccessful.
        These are separated by system- or data-disk types since they can work
        independently.

        Args:
            system_disk_execution_status (str): Standby|Executed|Failed
            data_disk_execution_status (str): Standby|Executed|Failed
        '''

        self.system_disk_execution_status = system_disk_execution_status
        self.data_disk_execution_status = data_disk_execution_status

    def __repr__(self):
        return u'<AutoSnapshotExecutionStatus at %s>' % id(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class AutoSnapshotPolicyStatus(object):

    def __init__(self, status, policy):
        self.status = status
        self.policy = policy

    def __repr__(self):
        return u'<AutoSnapshotPolicyStatus at %s>' % id(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class Disk(object):

    def __init__(self, disk_id, disk_type, disk_category, disk_size,
        attached_time=None, creation_time=None, delete_auto_snapshot=None,
        delete_with_instance=None, description=None, detached_time=None,
        device=None, image_id=None, instance_id=None, operation_locks=None,
        portable=None, product_code=None, snapshot_id=None, status=None,
        zone_id=None):

        """ECS Disk object. Required arguments are always required when creating
        an ECS disk.

        Args:
            disk_id (str): The id of the disk.
            disk_type (str): The type of disk.
                Values can be system or data.
            disk_category (str): The category of the disk.
                Values can be cloud, ephemeral
            disk_size (int): Its size in GB.
            attached_time (datetime): The time the disk was last attached.
            creation_time (datetime): The time the disk was created.
            delete_auto_snapshot (bool): Whether the AutoSnapshotPolicy will be
                                         deleted with the disk.
            delete_with_instance (bool): Whether the Disk will be deleted with
                                         its associated Instance.
            description (str): A long description of the disk.
            detached_time (datetie): The time the disk was last detached.
            device (str): The device path if attached. E.g. /dev/xvdb
            image_id (str): The Image id the Disk was created with.
            instance_id (str): The Instance id the disk is attached to.
            operation_locks (list): The locks on the resource. It can be
                                    'Financial' and/or 'Security'.
            portable (bool): Whether the Disk can be detached and re-attached
                             elsewhere.
            product_code (str): ID of the Disk in the ECS Mirror Market.
            snapshot_id (str): ID of the snapshot the Disk was created from.
            status (str): The status of the disk. E.g. "In_use", "Creating", &c.
            zone_id (str): The Availability Zone of the Disk.

        """
        if operation_locks is None:
            operation_locks = []
        self.disk_id = disk_id
        self.disk_type = disk_type
        self.disk_category = disk_category
        self.disk_size = disk_size
        self.attached_time = attached_time
        self.creation_time = creation_time
        self.delete_auto_snapshot = delete_auto_snapshot
        self.delete_with_instance = delete_with_instance
        self.description = description
        self.detached_time = detached_time
        self.device = device
        self.image_id = image_id
        self.instance_id = instance_id
        self.operation_locks = operation_locks
        self.portable = portable
        self.product_code = product_code
        self.snapshot_id = snapshot_id
        self.status = status
        self.zone_id = zone_id

    def __repr__(self):
        return u'<Disk %s of type %s is %sGB at %s>' % (
            self.disk_id, self.disk_type, self.disk_size, id(self))

    def __eq__(self, other):
        print self.__dict__
        print other.__dict__
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class DiskMappingError(Exception):
    """DiskMappingError"""


class DiskMapping(object):

    def __init__(self, category, size=None, snapshot_id=None, name=None,
                 description=None, device=None):
        """DiskMapping used to create and attach a disk to an instance.

        The disk can be created from either a size parameter or a snapshot_id.
        Different disk categories support different disk sizes, and snapshots
        need to be from the same category of disk you are creating. "cloud"
        disks support sizes between 5 and 2000 GB. "ephemeral" disks support 5
        to 1024 GB sizes.

        Args:
            category (str): "cloud" or "ephemeral". Usually "cloud". Check the
                            output of :method:`aliyun.ecs.connection.EcsConnection.describe_zones`
                            to see which categories of disks your zone supports.
            size (int): The size of the disk. Limits depend on category.
            snapshot_id (str): ID of :class:`.model.Snapshot` to create disk of.
            name (str): A short name for the disk, between 2 and 128 characters.
            description (str): A longer description of the disk. Between 2 and
                               256 characters.
            device (str): System device string. Leave None to defer to the system.
                          Valid choices are from /dev/xvdb to /dev/xvdz.
        Raises:
            DiskMappingError: If both size and snapshot are specified.
        """
        if None not in (size, snapshot_id):
            raise DiskMappingError("DiskMapping does not support both size AND snapshot. Choose one.")

        self.category = category
        self.size = size
        self.snapshot_id = snapshot_id
        self.name = name
        self.description = description
        self.device = device

    def api_dict(self, ordinal=1):
        """Serialize for insertion into API request parameters.

        Args:
            ordinal (int): The number of the data disk to serialize as.

        Returns:
            dict: A dictionary of URL GET query parameters to create the disk.
                  E.g.::

                      {
                          'DataDisk.1.Category': 'cloud',
                          'DataDisk.1.Size': 2000
                      }
        """
        ddisk = 'DataDisk.%s.' % ordinal
        out = {ddisk + 'Category': self.category}
        if self.size:
            out[ddisk + 'Size'] = self.size
        if self.snapshot_id:
            out[ddisk + 'SnapshotId'] = self.snapshot_id
        if self.name:
            out[ddisk + 'DiskName'] = self.name
        if self.description:
            out[ddisk + 'Description'] = self.description
        if self.device:
            out[ddisk + 'Device'] = self.device

        return out

    def __repr__(self):
        return u'<DiskMapping %s type %s at %s>' % (
            self.name, self.category, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class Image(object):

    def __init__(self, image_id, image_version, name, description, size,
            architecture, owner_alias, os_name):
        """Constructor.

        Args:
            image_id (str): The id of the image.
            image_version (str): The version of the image.
            name (str): Name of the image.
            description (str): The description.
            size (int): Its size in GB.
            architecture (str): The architecture - either i386 or x86_64.
            owner_alias (str): system, else or others.
            os_name (str): The os name.
        """
        self.image_id = image_id
        self.image_version = image_version
        self.description = description
        self.size = size
        self.architecture = architecture
        self.owner_alias = owner_alias
        self.os_name = os_name

    def __repr__(self):
        return u'<Image %s(%s) for platform %s and arch %s at %s>' % (
            self.image_id, self.description, self.os_name, self.architecture,
            id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class SecurityGroupInfo(object):

    def __init__(self, security_group_id, description):
        """Constructor.

        Args:
            security_group_id (str): The id of the security group.
            description (str): The description of the security group.
        """
        self.security_group_id = security_group_id
        self.description = description

    def __repr__(self):
        return u'<SecurityGroupInfo %s, %s at %s>' % (
            self.security_group_id, self.description, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class SecurityGroupPermission(object):

    def __init__(self, ip_protocol, port_range, source_cidr_ip,
                 source_group_id, policy, nic_type):
        """Constructor.

        Args:
            ip_protocol (str): TCP, UDP, ICMP, GRE or ALL
            port_range (str): For tcp/udp range is 1 to 65535. Else -1/-1.
            source_cidr_ip (str): Source IP address range.
            source_group_id (str): Source security group.
            policy (str): Accept, Drop or Reject.
            nic_type (str): internet or intranet.
        """
        self.ip_protocol = ip_protocol
        self.port_range = port_range
        self.source_cidr_ip = source_cidr_ip
        self.source_group_id = source_group_id
        self.policy = policy
        self.nic_type = nic_type

    def __repr__(self):
        return u'<SecurityGroupPermission %s %s %s from %s at %s>' % (
            self.policy, self.ip_protocol, self.port_range,
            self.source_cidr_ip
            if self.source_cidr_ip else self.source_group_id,
            id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class SecurityGroup(object):

    def __init__(self, region_id, security_group_id, description, permissions):
        """Constructor.

        Args:
            region_id (str): The id of the region for the security group.
            security_group_id (str): The id of the security group.
            description (str): The description of the security group.
            permission (list): List of SecurityGroupPermission.
        """
        self.region_id = region_id
        self.security_group_id = security_group_id
        self.description = description
        self.permissions = permissions

    def __repr__(self):
        return u'<SecurityGroup %s, %s at %s>' % (
            self.security_group_id, self.description, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class Zone(object):

    def __init__(self, zone_id, local_name, available_resource_creation=None,
            available_disk_types=None):
        """Constructor.

        Args:
            zone_id (str): The id of the zone.
            local_name (str): The local name of the zone.
            available_resource_creation (list of 'Instance' and/or 'Disk'): The resource types which can be created in this zone.
            available_disk_types (list of 'cloud' and/or 'ephemeral'): The types of disks which can be created in the zone.
        """
        if available_resource_creation is None:
            available_resource_creation = []
        if available_disk_types is None:
            available_disk_types = []
        self.zone_id = zone_id
        self.local_name = local_name
        self.available_resource_creation = available_resource_creation
        self.available_disk_types = available_disk_types

    def __repr__(self):
        return u'<Zone %s (%s) at %s>' % (
            self.zone_id, self.local_name, id(self))

    def disk_supported(self, disk_type):
        """Convenience method to say whether a disk type is supported.

        Args:
            disk_type (str): either 'cloud' or 'ephemeral'.

        Returns:
            boolean
        """
        return disk_type in self.available_disk_types

    def resource_creation_supported(self, resource_type):
        """Convenience method to say whether a resource can be created.

        Args:
            resource_type (str): either 'Instance' or 'Disk'

        Returns:
            Boolean. True if the resource creation is supported.
        """
        return resource_type in self.available_resource_creation

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)
