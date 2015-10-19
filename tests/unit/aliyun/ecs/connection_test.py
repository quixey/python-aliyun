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

import datetime
import dateutil.parser
import json
import mox
import time
import unittest
from aliyun.ecs.model import (
    AutoSnapshotPolicy,
    AutoSnapshotExecutionStatus,
    AutoSnapshotPolicyStatus,
    Disk,
    DiskMappingError,
    Image,
    Instance,
    InstanceStatus,
    InstanceType,
    SecurityGroup,
    SecurityGroupInfo,
    SecurityGroupPermission,
    Snapshot,
    Zone
)

from aliyun.ecs import connection as ecs


class MockEcsInstance(object):
    def __init__(self, instance_id, zone_id):
        self.instance_id = instance_id
        self.zone_id = zone_id


class EcsConnectionTest(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        self.conn = ecs.EcsConnection(region_id='r', access_key_id='a',
                                      secret_access_key='s')
        self.mox.StubOutWithMock(self.conn, 'get')

    def tearDown(self):
        self.mox.UnsetStubs()


class GetAllRegionsTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = {
            'Regions': {
                'Region': [
                    {'RegionId': 'r1', 'LocalName': 'l1'},
                    {'RegionId': 'r2', 'LocalName': 'l2'}
                ]
            }
        }
        expected_result = [ecs.Region('r1', 'l1'), ecs.Region('r2', 'l2')]
        self.conn.get({'Action': 'DescribeRegions'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result, self.conn.get_all_regions())
        self.mox.VerifyAll()

    def testGetIds(self):
        get_response = {
            'Regions': {
                'Region': [
                    {'RegionId': 'r1', 'LocalName': 'l1'},
                    {'RegionId': 'r2', 'LocalName': 'l2'}
                ]
            }
        }
        expected_result = ['r1', 'r2']
        self.conn.get({'Action': 'DescribeRegions'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result, self.conn.get_all_region_ids())
        self.mox.VerifyAll()


class GetAllZonesTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = {
            'Zones': {
                'Zone': [
                    {'ZoneId': 'z1', 'LocalName': 'l1',
                        'AvailableResourceCreation': {
                            'ResourceTypes': ['Disk', 'Instance']
                        },
                        'AvailableDiskCategories': {
                            'DiskCategories': ['cloud', 'ephemeral']
                        }
                    },
                    {'ZoneId': 'z2', 'LocalName': 'l2',
                        'AvailableResourceCreation': {
                            'ResourceTypes': ['Instance']
                        },
                        'AvailableDiskCategories': {
                            'DiskCategories': []
                        }
                    }]
                }
            }
        z1 = Zone('z1', 'l1', ['Disk', 'Instance'], ['cloud', 'ephemeral'])
        z2 = Zone('z2', 'l2', ['Instance'])
        self.conn.get({'Action': 'DescribeZones'}).AndReturn(get_response)
        self.mox.ReplayAll()

        self.assertEqual([z1, z2], self.conn.get_all_zones())

        self.mox.VerifyAll()

    def testZoneIds(self):
        z1 = Zone('z1', 'l1')
        z2 = Zone('z2', 'l2')
        self.mox.StubOutWithMock(self.conn, 'get_all_zones')
        self.conn.get_all_zones().AndReturn([z1, z2])
        self.mox.ReplayAll()

        self.assertEqual(['z1', 'z2'], self.conn.get_all_zone_ids())

        self.mox.VerifyAll()


class GetAllClustersTest(EcsConnectionTest):
    def testGetAllClusters(self):
        resp = {'Clusters': {'Cluster': [
            {'ClusterId': 'c1'},
            {'ClusterId': 'c2'}
            ]}}
        self.conn.get({'Action': 'DescribeClusters'}).AndReturn(resp)
        self.mox.ReplayAll()
        self.assertEqual(['c1', 'c2'], self.conn.get_all_clusters())
        self.mox.VerifyAll()


class GetAllInstanceStatusTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = [{
            'InstanceStatuses': {
                'InstanceStatus': [
                    {'InstanceId': 'i1', 'Status': 'running'},
                    {'InstanceId': 'i2', 'Status': 'stopped'}
                ]
            }
        },
            {
                'InstanceStatuses': {
                    'InstanceStatus': [
                        {'InstanceId': 'i3', 'Status': 'running'},
                    ]
                }
            }]
        expected_result = [InstanceStatus('i1', 'running'),
                           InstanceStatus('i2', 'stopped'),
                           InstanceStatus('i3', 'running')]
        self.conn.get({'Action': 'DescribeInstanceStatus', 'ZoneId': 'z'},
                      paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.get_all_instance_status(zone_id='z'))
        self.mox.VerifyAll()

    def testGetIds(self):
        get_response = [{
            'InstanceStatuses': {
                'InstanceStatus': [
                    {'InstanceId': 'i1', 'Status': 'running'},
                    {'InstanceId': 'i2', 'Status': 'stopped'}
                ]
            }
        },
            {
                'InstanceStatuses': {
                    'InstanceStatus': [
                        {'InstanceId': 'i3', 'Status': 'running'},
                    ]
                }
            }]
        expected_result = ['i1', 'i2', 'i3']
        self.conn.get({'Action': 'DescribeInstanceStatus'},
                      paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.get_all_instance_ids())
        self.mox.VerifyAll()


class GetInstanceTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = {
            'RegionId': 'r',
            'InstanceId': 'i1',
            'InstanceName': 'name',
            'ImageId': 'image',
            'InstanceType': 'type',
            'HostName': 'hostname',
            'Status': 'running',
            'InternetChargeType': 'chargetype',
            'InternetMaxBandwidthIn': '1',
            'InternetMaxBandwidthOut': '2',
            'CreationTime': '2014-02-05T00:52:32Z',
            'SecurityGroupIds': {'SecurityGroupId': ['sg1', 'sg2']},
            'PublicIpAddress': {'IpAddress': ['ip1', 'ip2']},
            'InnerIpAddress': {'IpAddress': ['ip3', 'ip4']},
            'Description': '',
            'ClusterId': '',
            'OperationLocks': {'LockReason': []},
            'ZoneId': 'z'
        }
        expected_result = Instance(
            'i1', 'name', 'image', 'r', 'type', 'hostname', 'running',
            ['sg1', 'sg2'], ['ip1', 'ip2'], ['ip3', 'ip4'], 'chargetype', 1, 2,
            dateutil.parser.parse('2014-02-05T00:52:32Z'), dateutil.parser.parse('2014-02-05T00:52:32Z'), '', '', '', [], 'z')
        self.conn.get({'Action': 'DescribeInstanceAttribute',
                       'InstanceId': 'i1'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.get_instance('i1'))
        self.mox.VerifyAll()


class InstanceActionsTest(EcsConnectionTest):

    def testStart(self):
        self.conn.get({'Action': 'StartInstance',
                       'InstanceId': 'i1'})

        self.mox.ReplayAll()
        self.conn.start_instance('i1')
        self.mox.VerifyAll()

    def testStop(self):
        self.conn.get({'Action': 'StopInstance',
                       'InstanceId': 'i1',
                       'ForceStop': 'false'})

        self.mox.ReplayAll()
        self.conn.stop_instance('i1')
        self.mox.VerifyAll()

    def testForceStop(self):
        self.conn.get({'Action': 'StopInstance',
                       'InstanceId': 'i1',
                       'ForceStop': 'true'})

        self.mox.ReplayAll()
        self.conn.stop_instance('i1', force=True)
        self.mox.VerifyAll()

    def testReboot(self):
        self.conn.get({'Action': 'RebootInstance',
                       'InstanceId': 'i1',
                       'ForceStop': 'false'})

        self.mox.ReplayAll()
        self.conn.reboot_instance('i1')
        self.mox.VerifyAll()

    def testForceReboot(self):
        self.conn.get({'Action': 'RebootInstance',
                       'InstanceId': 'i1',
                       'ForceStop': 'true'})

        self.mox.ReplayAll()
        self.conn.reboot_instance('i1', force=True)
        self.mox.VerifyAll()

    def testDelete(self):
        self.conn.get({'Action': 'DeleteInstance',
                       'InstanceId': 'i1'})

        self.mox.ReplayAll()
        self.conn.delete_instance('i1')
        self.mox.VerifyAll()

    def testReplaceSystemDisk(self):
        self.conn.get({
            'Action': 'ReplaceSystemDisk',
            'InstanceId': 'i',
            'ImageId': 'img'}).AndReturn({'DiskId': 'd'})
        self.mox.ReplayAll()
        self.assertEqual('d', self.conn.replace_system_disk('i', 'img'))
        self.mox.VerifyAll()

    def testJoinSecurityGroup(self):
        self.conn.get({'Action': 'JoinSecurityGroup',
                       'InstanceId': 'i1',
                       'SecurityGroupId': 'sg1'})

        self.mox.ReplayAll()
        self.conn.join_security_group('i1', 'sg1')
        self.mox.VerifyAll()

    def testLeaveSecurityGroup(self):
        self.conn.get({'Action': 'LeaveSecurityGroup',
                       'InstanceId': 'i1',
                       'SecurityGroupId': 'sg1'})

        self.mox.ReplayAll()
        self.conn.leave_security_group('i1', 'sg1')
        self.mox.VerifyAll()


class DiskActionsTest(EcsConnectionTest):

    def testCreateDiskSizeFull(self):
        self.conn.get({'Action': 'CreateDisk',
                       'ZoneId': 'z1',
                       'DiskName': 'name',
                       'Description': 'desc',
                       'Size': 5}).AndReturn({'DiskId': 'd'})
        self.mox.ReplayAll()
        self.conn.create_disk('z1', 'name', 'desc', 5, None)
        self.mox.VerifyAll()

    def testCreateDiskSnapshot(self):
        self.conn.get({'Action': 'CreateDisk',
                       'ZoneId': 'z1',
                       'SnapshotId': 'snap'}).AndReturn({'DiskId': 'd1'})
        self.mox.ReplayAll()
        self.assertEqual('d1', self.conn.create_disk('z1', snapshot_id='snap'))
        self.mox.VerifyAll()

    def testAttachDisk(self):
        self.conn.get({'Action': 'AttachDisk',
                       'InstanceId': 'i1',
                       'Device': 'dev',
                       'DeleteWithInstance': True,
                       'DiskId': 'd1'})
        self.mox.ReplayAll()
        self.conn.attach_disk('i1', 'd1', 'dev', True)
        self.mox.VerifyAll()

    def testAddDisk(self):
        self.mox.StubOutWithMock(self.conn, 'get_instance')
        self.conn.get_instance('i1').AndReturn(MockEcsInstance('i1', 'z1'))
        self.mox.StubOutWithMock(self.conn, 'create_disk')
        self.conn.create_disk('z1', 'name', 'desc', None, 'snap').AndReturn('d')
        self.mox.StubOutWithMock(self.conn, 'attach_disk')
        self.conn.attach_disk('i1', 'd', 'dev', True)
        self.mox.ReplayAll()

        d = self.conn.add_disk('i1', None, 'snap', 'name', 'desc', 'dev', True)
        self.assertEqual(d, 'd')

        self.mox.VerifyAll()

    def testResetDisk(self):
        self.conn.get({'Action': 'ResetDisk', 'DiskId': 'd', 'SnapshotId': 's'})
        self.mox.ReplayAll()
        self.conn.reset_disk('d', 's')
        self.mox.VerifyAll()

    def testDeleteDisk(self):
        self.conn.get({'Action': 'DeleteDisk',
                       'DiskId': 'd1'})
        self.mox.ReplayAll()
        self.conn.delete_disk('d1')
        self.mox.VerifyAll()

    def testCreateDiskArgs(self):
        try:
            self.conn.create_disk('i1', size=5, snapshot_id='snap')
        except ecs.Error, e:
            self.assertTrue(e.message.startswith("Use size or snapshot_id."))

    def testDetachDisk(self):
        self.conn.get({'Action': 'DetachDisk',
                       'InstanceId': 'i',
                       'DiskId': 'd'})
        self.mox.ReplayAll()

        self.conn.detach_disk('i', 'd')

        self.mox.VerifyAll()

    def testModifyDisk(self):
        self.conn.get({'Action': 'ModifyDiskAttribute',
                       'DiskId': 'd',
                       'DiskName': 'name',
                       'Description': 'desc',
                       'DeleteWithInstance': True})
        self.mox.ReplayAll()
        self.conn.modify_disk('d', 'name', 'desc', True)
        self.mox.VerifyAll()

    def testReInitDisk(self):
        self.conn.get({'Action': 'ReInitDisk', 'DiskId': 'd'})
        self.mox.ReplayAll()
        self.conn.reinit_disk('d')
        self.mox.VerifyAll()

    def testInstanceDisks(self):
        d1 = Disk('d1', 'system', 'cloud', 20)
        d2 = Disk('d2', 'system', 'cloud', 20)
        d3 = Disk('d3', 'system', 'cloud', 20)
        self.mox.StubOutWithMock(self.conn, 'describe_disks')
        self.conn.describe_disks(instance_id='i').AndReturn([d1, d2, d3])
        self.mox.ReplayAll()
        self.assertEqual([d1, d2, d3], self.conn.describe_instance_disks('i'))
        self.mox.VerifyAll()


class ModifyInstanceTest(EcsConnectionTest):

    def testModifyAll(self):
        self.conn.get({'Action': 'ModifyInstanceAttribute',
                       'InstanceId': 'i1',
                       'InstanceName': 'name',
                       'Password': 'pw',
                       'HostName': 'name',
                       'SecurityGroupId': 'sg1',
                       'Description': 'desc'})

        self.mox.ReplayAll()
        self.conn.modify_instance(
            'i1', new_instance_name='name', new_password='pw',
            new_hostname='name', new_security_group_id='sg1',
            new_description='desc')
        self.mox.VerifyAll()


class ModifyInstanceSpecTest(EcsConnectionTest):

    def testModifyInstanceSpecType(self):
        self.conn.get({'Action': 'ModifyInstanceSpec',
                       'InstanceId': 'i1',
                       'InstanceType': 'type1'})

        self.mox.ReplayAll()
        self.conn.modify_instance_spec('i1', instance_type='type1')
        self.mox.VerifyAll()

    def testModifyInstanceSpecNetIn(self):
        self.conn.get({'Action': 'ModifyInstanceSpec',
                       'InstanceId': 'i1',
                       'InternetMaxBandwidthIn': 1})

        self.mox.ReplayAll()
        self.conn.modify_instance_spec('i1', internet_max_bandwidth_in=1)
        self.mox.VerifyAll()

    def testModifyInstanceSpecNetOut(self):
        self.conn.get({'Action': 'ModifyInstanceSpec',
                       'InstanceId': 'i1',
                       'InternetMaxBandwidthOut': 1})

        self.mox.ReplayAll()
        self.conn.modify_instance_spec('i1', internet_max_bandwidth_out=1)
        self.mox.VerifyAll()

    def testModifyInstanceSpecAll(self):
        self.conn.get({'Action': 'ModifyInstanceSpec',
                       'InstanceId': 'i1',
                       'InstanceType': 'type1',
                       'InternetMaxBandwidthIn': 1,
                       'InternetMaxBandwidthOut': 2})

        self.mox.ReplayAll()
        self.conn.modify_instance_spec('i1', instance_type='type1',
                                       internet_max_bandwidth_in=1,
                                       internet_max_bandwidth_out=2)
        self.mox.VerifyAll()


class CreateInstanceTest(EcsConnectionTest):

    def testMinimalParams(self):
        get_response = {'InstanceId': 'i1'}
        self.conn.get({'Action': 'CreateInstance',
                       'ImageId': 'image',
                       'SecurityGroupId': 'sg1',
                       'InstanceType': 'type'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(
            'i1',
            self.conn.create_instance('image', 'type', 'sg1'))
        self.mox.VerifyAll()

    def testMinimalDisks(self):
        get_response = {'InstanceId': 'i1'}
        self.conn.get({'Action': 'CreateInstance',
                       'ImageId': 'image',
                       'SecurityGroupId': 'sg1',
                       'InstanceType': 'type',
                       'DataDisk.1.Category': 'cloud',
                       'DataDisk.1.Size': 1024}).AndReturn(get_response)
        self.mox.ReplayAll()
        disks = [('cloud', 1024)]
        self.assertEqual(
            'i1',
            self.conn.create_instance('image', 'type', 'sg1', data_disks=disks))

        self.mox.VerifyAll()

    def testConflictingDisk(self):
        self.mox.ReplayAll()
        disks = [('cloud', 1024, 'snap')]
        try:
            self.conn.create_instance('image', 'type', 'sg1', data_disks=disks)
        except DiskMappingError, e:
            self.assertTrue(e.__class__.__name__ == 'DiskMappingError')

        self.mox.VerifyAll()

    def testAllParams(self):
        get_response = {'InstanceId': 'i1'}
        self.conn.get({'Action': 'CreateInstance',
                       'ImageId': 'image',
                       'SecurityGroupId': 'sg1',
                       'InstanceType': 'type',
                       'InstanceName': 'name',
                       'InternetMaxBandwidthIn': '1',
                       'InternetMaxBandwidthOut': '2',
                       'HostName': 'hname',
                       'Password': 'pw',
                       'SystemDisk.Category': 'cloud',
                       'InternetChargeType': 'PayByBandwidth',
                       'DataDisk.1.Category': 'cloud',
                       'DataDisk.1.Size': 5,
                       'DataDisk.1.Description': 'dd-1-desc',
                       'DataDisk.1.DiskName': 'dd-1-name',
                       'DataDisk.1.Device': '/dev/xvd-testing',
                       'DataDisk.2.Category': 'ephemeral',
                       'DataDisk.2.SnapshotId': 'snap',
                       'Description': 'desc',
                       'ZoneId': 'test-zone-a'}).AndReturn(
            get_response)

        disks = [
            {
                'category': 'cloud',
                'size': 5,
                'description': 'dd-1-desc',
                'name': 'dd-1-name',
                'device': '/dev/xvd-testing'
            },
            {'category': 'ephemeral', 'snapshot_id': 'snap'}
        ]
        self.mox.ReplayAll()
        self.assertEqual(
            'i1',
            self.conn.create_instance(
                'image', 'type', 'sg1', instance_name='name',
                internet_max_bandwidth_in=1, internet_max_bandwidth_out=2,
                hostname='hname', password='pw', system_disk_type='cloud',
                internet_charge_type='PayByBandwidth',
                data_disks=disks, description='desc', zone_id='test-zone-a'))
        self.mox.VerifyAll()


class CreateAndStartInstanceTest(EcsConnectionTest):

    def setUp(self):
        super(CreateAndStartInstanceTest, self).setUp()
        self.mox.StubOutWithMock(self.conn, 'create_instance')
        self.mox.StubOutWithMock(self.conn, 'join_security_group')
        self.mox.StubOutWithMock(self.conn, 'start_instance')
        self.mox.StubOutWithMock(self.conn, 'get_instance')
        self.mox.StubOutWithMock(time, 'sleep')

    def testTooManySecurityGroups(self):
        try:
            self.conn.create_and_start_instance(
                'image', 'type', 'sg1',
                additional_security_group_ids=[
                    'sg2', 'sg3', 'sg4', 'sg5', 'sg6'])
            self.fail('Should throw error if too many security groups')
        except ecs.Error as err:
            self.assertTrue('max 5' in str(err))

    def testWithMinimalParams(self):
        self.conn.create_instance(
            'image', 'type', 'sg1',
            hostname=None, instance_name=None, internet_charge_type=None,
            internet_max_bandwidth_in=None, internet_max_bandwidth_out=None,
            password=None, system_disk_type=None, data_disks=[],
            description=None, zone_id=None).AndReturn('i1')
        self.conn.get({
            'Action': 'AllocatePublicIpAddress',
            'InstanceId': 'i1'
        })
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        self.mox.ReplayAll()
        self.assertEqual('i1', self.conn.create_and_start_instance(
            'image', 'type', 'sg1', block_till_ready=False))
        self.mox.VerifyAll()

    def testWithAllParams(self):
        self.conn.create_instance(
            'image', 'type', 'sg1', instance_name='name',
            internet_max_bandwidth_in=1, internet_max_bandwidth_out=2,
            hostname='hname', password='pw', system_disk_type='cloud',
            internet_charge_type='PayByBandwidth',
            data_disks=[('cloud', 5)], description='desc',
            zone_id='test-zone-a').AndReturn('i1')
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        self.mox.ReplayAll()
        self.assertEqual('i1', self.conn.create_and_start_instance(
            'image', 'type', 'sg1', instance_name='name',
            internet_max_bandwidth_in=1, internet_max_bandwidth_out=2,
            hostname='hname', password='pw', system_disk_type='cloud',
            internet_charge_type='PayByBandwidth', assign_public_ip=False,
            block_till_ready=False, data_disks=[('cloud', 5)],
            description='desc', zone_id='test-zone-a'))
        self.mox.VerifyAll()

    def testWithAdditionalSecurityGroupsNoBlock(self):
        self.conn.create_instance(
            'image', 'type', 'sg1',
            hostname=None, instance_name=None, internet_charge_type=None,
            internet_max_bandwidth_in=None, internet_max_bandwidth_out=None,
            password=None, system_disk_type=None, data_disks=[],
            description=None, zone_id=None).AndReturn('i1')
        time.sleep(mox.IsA(int))
        self.conn.join_security_group('i1', 'sg2')
        self.conn.join_security_group('i1', 'sg3')
        self.conn.get({
            'Action': 'AllocatePublicIpAddress',
            'InstanceId': 'i1'
        })
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        self.mox.ReplayAll()
        self.assertEqual('i1', self.conn.create_and_start_instance(
            'image', 'type', 'sg1',
            additional_security_group_ids=['sg2', 'sg3'],
            block_till_ready=False))
        self.mox.VerifyAll()

    def testWithBlocking(self):
        instance_starting = Instance(
            'i1', None, None, None, None, None, 'Starting', None,
            None, None, None, None, None, None, None, None, None, None, None, None)
        instance_running = Instance(
            'i1', None, None, None, None, None, 'Running', None,
            None, None, None, None, None, None, None, None, None, None, None, None)
        self.conn.create_instance(
            'image', 'type', 'sg1',
            hostname=None, instance_name=None, internet_charge_type=None,
            internet_max_bandwidth_in=None, internet_max_bandwidth_out=None,
            password=None, system_disk_type=None, data_disks=[],
            description=None, zone_id=None).AndReturn('i1')
        self.conn.get({
            'Action': 'AllocatePublicIpAddress',
            'InstanceId': 'i1'
        })
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_starting)
        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_starting)
        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_running)

        self.mox.ReplayAll()
        self.assertEqual('i1', self.conn.create_and_start_instance(
            'image', 'type', 'sg1'))
        self.mox.VerifyAll()

    def testWithBlockingTimesOut(self):
        instance_starting = Instance(
            'i1', None, None, None, None, None, 'Starting', None,
            None, None, None, None, None, None, None, None, None, None, None, None)
        self.conn.create_instance(
            'image', 'type', 'sg1',
            hostname=None, instance_name=None, internet_charge_type=None,
            internet_max_bandwidth_in=None, internet_max_bandwidth_out=None,
            password=None, system_disk_type=None, data_disks=[],
            description=None, zone_id=None).AndReturn('i1')
        self.conn.get({
            'Action': 'AllocatePublicIpAddress',
            'InstanceId': 'i1'
        })
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        time.sleep(mox.IsA(int)).MultipleTimes()
        self.conn.get_instance('i1').MultipleTimes().AndReturn(
            instance_starting)

        self.mox.ReplayAll()
        try:
            self.conn.create_and_start_instance('image', 'type', 'sg1')
            self.fail('Should throw error if times out')
        except ecs.Error as err:
            self.assertTrue('Timed out' in str(err))
        self.mox.VerifyAll()

    def testWithAdditionalSecurityGroupsBlocking(self):
        instance_starting = Instance(
            'i1', None, None, None, None, None, 'Starting', None,
            None, None, None, None, None, None, None, None, None, None, None, None)
        instance_running = Instance(
            'i1', None, None, None, None, None, 'Running', None,
            None, None, None, None, None, None, None, None, None, None, None, None)
        self.conn.create_instance(
            'image', 'type', 'sg1',
            hostname=None, instance_name=None, internet_charge_type=None,
            internet_max_bandwidth_in=None, internet_max_bandwidth_out=None,
            password=None, system_disk_type=None, data_disks=[],
            description=None, zone_id=None).AndReturn('i1')
        time.sleep(mox.IsA(int))
        self.conn.join_security_group('i1', 'sg2')
        self.conn.join_security_group('i1', 'sg3')
        self.conn.get({
            'Action': 'AllocatePublicIpAddress',
            'InstanceId': 'i1'
        })
        time.sleep(mox.IsA(int))
        self.conn.start_instance('i1')

        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_starting)
        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_starting)
        time.sleep(mox.IsA(int))
        self.conn.get_instance('i1').AndReturn(instance_running)

        self.mox.ReplayAll()
        self.assertEqual('i1', self.conn.create_and_start_instance(
            'image', 'type', 'sg1',
            additional_security_group_ids=['sg2', 'sg3']))
        self.mox.VerifyAll()


class DescribeInstanceTypesTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = {
            'InstanceTypes': {
                'InstanceType': [
                    {'InstanceTypeId': 't1', 'CpuCoreCount': '2',
                     'MemorySize': '4'},
                    {'InstanceTypeId': 't2', 'CpuCoreCount': '4',
                     'MemorySize': '4'}
                ]
            }
        }
        expected_result = [InstanceType('t1', 2, 4),
                           InstanceType('t2', 4, 4)]
        self.conn.get({'Action': 'DescribeInstanceTypes'}).AndReturn(
            get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result, self.conn.describe_instance_types())
        self.mox.VerifyAll()


class DescribeDisksTest(EcsConnectionTest):

    def testSuccess(self):
        now = "2014-09-03T23:37:37Z"
        get_response = [{
            'Disks': {
                'Disk': [
                    {
                        "AttachedTime": now,
                        "Category": "cloud",
                        "CreationTime": now,
                        "DeleteAutoSnapshot": "true",
                        "DeleteWithInstance": "true",
                        "Description": "",
                        "DetachedTime": "",
                        "Device": "/dev/xvda",
                        "DiskId": "d1",
                        "DiskName": "",
                        "ImageId": "image-id.vhd",
                        "InstanceId": "i-id",
                        "OperationLocks": {
                            "OperationLock": []
                        },
                        "Portable": "false",
                        "ProductCode": "",
                        "Size":20,
                        "SourceSnapshotId": "",
                        "Status": "In_use",
                        "Type": "system",
                        "ZoneId": "zid"
                    },
                    {
                        "AttachedTime": now,
                        "Category": "ephemeral",
                        "CreationTime": now,
                        "DeleteAutoSnapshot": "true",
                        "DeleteWithInstance": "true",
                        "Description": "",
                        "DetachedTime": "",
                        "Device": "/dev/xvda",
                        "DiskId": "d2",
                        "DiskName": "",
                        "ImageId": "image-id.vhd",
                        "InstanceId": "i-id",
                        "OperationLocks": {
                            "OperationLock": []
                        },
                        "Portable": "false",
                        "ProductCode": "",
                        "Size":100,
                        "SourceSnapshotId": "",
                        "Status": "In_use",
                        "Type": "data",
                        "ZoneId": "zid"
                    }
                ]
            }
        }, {
            'Disks': {
                'Disk': [
                    {
                        "AttachedTime": "",
                        "Category": "cloud",
                        "CreationTime": "",
                        "DeleteAutoSnapshot": "",
                        "DeleteWithInstance": "",
                        "Description": "",
                        "DetachedTime": "",
                        "Device": "",
                        "DiskId": "d3",
                        "DiskName": "",
                        "ImageId": "",
                        "InstanceId": "",
                        "OperationLocks": {
                            "OperationLock": []
                        },
                        "Portable": "",
                        "ProductCode": "",
                        "Size":20,
                        "SourceSnapshotId": "",
                        "Status": "",
                        "Type": "system",
                        "ZoneId": ""
                    }
                ]
            }
        }]
        nowtime = dateutil.parser.parse(now)
        d1 = Disk('d1', 'system', 'cloud', 20, nowtime, nowtime, True, True, None,
                  None, '/dev/xvda', 'image-id.vhd', 'i-id', [], False, None, None,
                  'In_use', 'zid')
        d2 = Disk('d2', 'data', 'ephemeral', 100, nowtime, nowtime, True, True, None,
                  None, '/dev/xvda', 'image-id.vhd', 'i-id', [], False, None, None,
                  'In_use', 'zid')
        d3 = Disk('d3', 'system', 'cloud', 20)
        self.conn.get({'Action': 'DescribeDisks',
                       'InstanceId': 'i-id',
                       'DiskIds': 'd,d',
                       'ZoneId': 'z'}, paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(
            [d1, d2, d3],
            self.conn.describe_disks(instance_id='i-id', zone_id='z', disk_ids=['d','d']))
        self.mox.VerifyAll()


class AutoSnapshotPolicyTest(EcsConnectionTest):

    def testDescribeAutoSnapshotPolicy(self):
        response = {
            "AutoSnapshotExcutionStatus": {
                "DataDiskExcutionStatus": "Executed",
                "SystemDiskExcutionStatus": "Executed"
            },
            "AutoSnapshotPolicy": {
                "SystemDiskPolicyEnabled": "true",
                "SystemDiskPolicyTimePeriod": "1",
                "SystemDiskPolicyRetentionDays": "2",
                "SystemDiskPolicyRetentionLastWeek": "true",
                "DataDiskPolicyEnabled": "true",
                "DataDiskPolicyTimePeriod": "3",
                "DataDiskPolicyRetentionDays": "4",
                "DataDiskPolicyRetentionLastWeek": "true"
            },
            "RequestId": ""
        }
        policy = AutoSnapshotPolicy(True, 1, 2, True, True, 3, 4, True)
        status = AutoSnapshotExecutionStatus('Executed', 'Executed')
        policystatus = AutoSnapshotPolicyStatus(status, policy)
        self.conn.get({'Action': 'DescribeAutoSnapshotPolicy'}).AndReturn(response)
        self.mox.ReplayAll()

        self.assertEqual(self.conn.describe_auto_snapshot_policy(), policystatus)

        self.mox.VerifyAll()

    def testModifyAutoSnapshotPolicy(self):
        self.conn.get({
            'Action': 'ModifyAutoSnapshotPolicy',
            'SystemDiskPolicyEnabled': 'true',
            'SystemDiskPolicyTimePeriod': 1,
            'SystemDiskPolicyRetentionDays': 2,
            'SystemDiskPolicyRetentionLastWeek': 'true',
            'DataDiskPolicyEnabled': 'true',
            'DataDiskPolicyTimePeriod': 3,
            'DataDiskPolicyRetentionDays': 4,
            'DataDiskPolicyRetentionLastWeek': 'true'
            })
        self.mox.ReplayAll()
        self.conn.modify_auto_snapshot_policy(True, 1, 2, True, True, 3, 4, True)
        self.mox.VerifyAll()


class DeleteSnapshotTest(EcsConnectionTest):

    def testSuccess(self):
        self.conn.get({'Action': 'DeleteSnapshot',
                       'InstanceId': 'i1',
                       'SnapshotId': 's1'})

        self.mox.ReplayAll()
        self.conn.delete_snapshot('i1', 's1')
        self.mox.VerifyAll()


class DescribeSnapshotTest(EcsConnectionTest):

    def testSuccess(self):
        # describe_snapshot is a simple wrapper around describe_snapshots
        self.mox.StubOutWithMock(self.conn, 'describe_snapshots')
        self.conn.describe_snapshots(snapshot_ids=['s-snap']).AndReturn(['thing'])
        self.mox.ReplayAll()
        self.assertEqual(self.conn.describe_snapshot('s-snap'), 'thing')
        self.mox.VerifyAll()

    def testFailure(self):
        # describe_snapshot is a simple wrapper around describe_snapshots
        self.mox.StubOutWithMock(self.conn, 'describe_snapshots')
        self.conn.describe_snapshots(snapshot_ids=['s-snap']).AndReturn([])
        self.mox.ReplayAll()
        try:
            self.conn.describe_snapshot('s-snap')
        except ecs.Error, e:
            self.assertTrue(e.message.startswith('Could not find'))

        self.mox.VerifyAll()

class DescribeSnapshotsTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = [
            {"Snapshots": {
                "Snapshot": [
                    {
                        "CreationTime": "2014-09-22T20:21:41Z",
                        "Description": "desc1",
                        "ProductCode": "",
                        "Progress": "100%",
                        "SnapshotId": "s1",
                        "SnapshotName": "auto1",
                        "SourceDiskId": "d1",
                        "SourceDiskSize": "20",
                        "SourceDiskType": "system"
                    },
                    {
                        "CreationTime": "2014-09-22T20:21:41Z",
                        "Description": "desc2",
                        "ProductCode": "",
                        "Progress": "100%",
                        "SnapshotId": "s2",
                        "SnapshotName": "auto2",
                        "SourceDiskId": "d2",
                        "SourceDiskSize": "20",
                        "SourceDiskType": "system"
                    }
                ]
            }},
            {"Snapshots": {
                "Snapshot": [
                    {
                        "CreationTime": "2014-09-22T20:21:41Z",
                        "Description": "desc3",
                        "ProductCode": "",
                        "Progress": "100%",
                        "SnapshotId": "s3",
                        "SnapshotName": "auto3",
                        "SourceDiskId": "d3",
                        "SourceDiskSize": "20",
                        "SourceDiskType": "system"
                    }
                ]
            }}
        ]

        now = dateutil.parser.parse('2014-09-22T20:21:41Z')
        expected_result = [
            ecs.Snapshot('s1', 'auto1', 100, now, 'desc1', 'd1', 'system', 20),
            ecs.Snapshot('s2', 'auto2', 100, now, 'desc2', 'd2', 'system', 20),
            ecs.Snapshot('s3', 'auto3', 100, now, 'desc3', 'd3', 'system', 20),
            ]
        params = {
            'Action': 'DescribeSnapshots',
            'InstanceId': 'iid',
            'DiskId': 'did',
            'SnapshotIds': json.dumps(['s1', 's2', 's3'])
        }
        self.conn.get(params, paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        results = self.conn.describe_snapshots('iid', 'did', ['s1', 's2', 's3'])
        self.assertEqual(expected_result, results)
        self.mox.VerifyAll()


class CreateSnapshotTest(EcsConnectionTest):

    def setUp(self):
        super(CreateSnapshotTest, self).setUp()
        self.mox.StubOutWithMock(self.conn, 'describe_snapshot')
        self.mox.StubOutWithMock(time, 'sleep')

    def testNoBlocking(self):
        get_response = {
            'SnapshotId': 's1'
        }
        self.conn.get({'Action': 'CreateSnapshot',
                       'InstanceId': 'i1',
                       'DiskId': 'd1'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual('s1', self.conn.create_snapshot('i1', 'd1'))
        self.mox.VerifyAll()

    def testNoBlockingWithParams(self):
        get_response = {
            'SnapshotId': 's1'
        }
        self.conn.get({'Action': 'CreateSnapshot',
                       'InstanceId': 'i1',
                       'DiskId': 'd1',
                       'Description': 'desc',
                       'SnapshotName': 'n'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual('s1', self.conn.create_snapshot(
            'i1', 'd1', snapshot_name='n', description='desc'))
        self.mox.VerifyAll()

    def testBlockingTimesOut(self):
        get_response = {
            'SnapshotId': 's1'
        }
        incomplete_snapshot = ecs.Snapshot('s1', None, 99,
                                           datetime.datetime.now())
        self.conn.get({'Action': 'CreateSnapshot',
                       'InstanceId': 'i1',
                       'DiskId': 'd1'}).AndReturn(get_response)
        time.sleep(mox.IsA(int)).MultipleTimes()
        self.conn.describe_snapshot('s1').MultipleTimes().AndReturn(
            incomplete_snapshot)

        self.mox.ReplayAll()
        try:
            self.conn.create_snapshot(
                'i1', 'd1', timeout_secs=300)
            self.fail('Should error out on timeout')
        except ecs.Error as err:
            self.assertTrue('not ready' in str(err))
        self.mox.VerifyAll()

    def testBlockingSucceeds(self):
        get_response = {
            'SnapshotId': 's1'
        }
        incomplete_snapshot = ecs.Snapshot('s1', None, 99,
                                           datetime.datetime.now())
        complete_snapshot = ecs.Snapshot('s1', None, 100,
                                         datetime.datetime.now())
        self.conn.get({'Action': 'CreateSnapshot',
                       'InstanceId': 'i1',
                       'DiskId': 'd1'}).AndReturn(get_response)
        time.sleep(mox.IsA(int))
        self.conn.describe_snapshot('s1').AndReturn(
            incomplete_snapshot)
        time.sleep(mox.IsA(int))
        self.conn.describe_snapshot('s1').AndReturn(
            incomplete_snapshot)
        time.sleep(mox.IsA(int))
        self.conn.describe_snapshot('s1').AndReturn(
            complete_snapshot)

        self.mox.ReplayAll()
        self.assertEqual('s1', self.conn.create_snapshot(
            'i1', 'd1', timeout_secs=300))
        self.mox.VerifyAll()


class DescribeImagesTest(EcsConnectionTest):

    def testSimpleQuery(self):
        get_response = [
            {
                "Images": {
                    "Image": [
                        {
                            "Architecture": "arch",
                            "CreationTime": "time",
                            "Description": "desc",
                            "DiskDeviceMappings": {
                                "DiskDeviceMapping": [
                                    {
                                        "Device": "/dev/xvda",
                                        "Size": 20,
                                        "SnapshotId": ""
                                    }
                                ]
                            },
                            "ImageId": "i1",
                            "ImageName": "name",
                            "ImageOwnerAlias": "owner",
                            "ImageVersion": "version",
                            "IsSubscribed": False,
                            "OSName": "os",
                            "ProductCode": "productcode",
                            "Size": 20
                        }
                    ]
                }
            },
            {
                "Images": {
                    "Image": [
                        {
                            "Architecture": "arch",
                            "CreationTime": "time",
                            "Description": "desc",
                            "DiskDeviceMappings": {
                                "DiskDeviceMapping": [
                                    {
                                        "Device": "/dev/xvda",
                                        "Size": 20,
                                        "SnapshotId": ""
                                    }
                                ]
                            },
                            "ImageId": "i2",
                            "ImageName": "name",
                            "ImageOwnerAlias": "owner",
                            "ImageVersion": "version",
                            "IsSubscribed": False,
                            "OSName": "os",
                            "ProductCode": "productcode",
                            "Size": 20
                        }
                    ]
                }
            }
        ]
        expected_result = [
            Image('i1', 'version', 'name', 'desc', 20, 'arch', 'owner', 'os'),
            Image('i2', 'version', 'name', 'desc', 20, 'arch', 'owner', 'os'),
        ]
        self.conn.get({
            'Action': 'DescribeImages',
            'ImageId': 'i1,i2',
            'ImageOwnerAlias': 'system',
            'SnapshotId': 'snap'}, paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.describe_images(['i1', 'i2'], ['system'],'snap'))
        self.mox.VerifyAll()


class DeleteImageTest(EcsConnectionTest):

    def testSuccess(self):
        self.conn.get({'Action': 'DeleteImage',
                       'ImageId': 'i1'})

        self.mox.ReplayAll()
        self.conn.delete_image('i1')
        self.mox.VerifyAll()


class CreateImageTest(EcsConnectionTest):

    def testSimple(self):
        get_response = {
            'ImageId': 'i1'
        }

        self.conn.get({'Action': 'CreateImage',
                       'SnapshotId': 's1'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.conn.create_image('s1')
        self.mox.VerifyAll()

    def testWithParams(self):
        get_response = {
            'ImageId': 'i1'
        }

        self.conn.get({'Action': 'CreateImage',
                       'SnapshotId': 's1',
                       'ImageVersion': '1.0',
                       'Description': 'desc',
                       'OSName': 'os'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.conn.create_image('s1', image_version='1.0',
                               description='desc', os_name='os')
        self.mox.VerifyAll()


class CreateImageFromInstanceTest(EcsConnectionTest):

    def setUp(self):
        super(CreateImageFromInstanceTest, self).setUp()
        self.mox.StubOutWithMock(self.conn, 'describe_instance_disks')
        self.mox.StubOutWithMock(self.conn, 'create_snapshot')
        self.mox.StubOutWithMock(self.conn, 'create_image')
        self.mox.StubOutWithMock(time, 'sleep')

    def testSystemDiskNotFound(self):
        data_disk = Disk('d2', 'data', 'ephemeral', 100)
        self.conn.describe_instance_disks('i1').AndReturn([data_disk])

        self.mox.ReplayAll()
        try:
            self.conn.create_image_from_instance('i1')
            self.fail('Should throw error if system disk not found')
        except ecs.Error as err:
            self.assertTrue('not found' in str(err))
        self.mox.VerifyAll()

    def testSuccess(self):
        data_disk = Disk('d2', 'data', 'ephemeral', 100)
        system_disk = Disk('d1', 'system', 'cloud', 100)
        self.conn.describe_instance_disks('i1').AndReturn(
            [data_disk, system_disk])
        self.conn.create_snapshot(
            'i1', 'd1', timeout_secs=mox.IsA(int)).AndReturn('s1')
        self.conn.create_image('s1', image_version=None, description=None,
                               os_name=None).AndReturn('img1')
        time.sleep(mox.IsA(int))

        self.mox.ReplayAll()
        self.assertEqual(('s1', 'img1'),
                         self.conn.create_image_from_instance('i1'))
        self.mox.VerifyAll()

    def testFullParams(self):
        data_disk = Disk('d2', 'data', 'ephemeral', 100)
        system_disk = Disk('d1', 'system', 'cloud', 100)
        self.conn.describe_instance_disks('i1').AndReturn(
            [data_disk, system_disk])
        self.conn.create_snapshot(
            'i1', 'd1', timeout_secs=301).AndReturn('s1')
        self.conn.create_image('s1', image_version='1.0', description='d',
                               os_name='ubuntu').AndReturn('img1')
        time.sleep(mox.IsA(int))

        self.mox.ReplayAll()
        self.assertEqual(('s1', 'img1'),
                         self.conn.create_image_from_instance(
                             'i1', image_version='1.0', description='d',
                             os_name='ubuntu', timeout_secs=301))
        self.mox.VerifyAll()


class DescribeSecurityGroupsTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = [{
            'SecurityGroups': {
                'SecurityGroup': [
                    {'SecurityGroupId': 'sg1', 'Description': 'd1'},
                    {'SecurityGroupId': 'sg2', 'Description': None}
                ]
            }
        },
            {
                'SecurityGroups': {
                    'SecurityGroup': [
                        {'SecurityGroupId': 'sg3', 'Description': 'd3'},
                    ]
                }
            }]
        expected_result = [SecurityGroupInfo('sg1', 'd1'),
                           SecurityGroupInfo('sg2', None),
                           SecurityGroupInfo('sg3', 'd3')]
        self.conn.get({'Action': 'DescribeSecurityGroups'},
                      paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.describe_security_groups())
        self.mox.VerifyAll()

    def testGetIds(self):
        get_response = [{
            'SecurityGroups': {
                'SecurityGroup': [
                    {'SecurityGroupId': 'sg1', 'Description': 'd1'},
                    {'SecurityGroupId': 'sg2', 'Description': None}
                ]
            }
        },
            {
                'SecurityGroups': {
                    'SecurityGroup': [
                        {'SecurityGroupId': 'sg3', 'Description': 'd3'},
                    ]
                }
            }]
        expected_result = ['sg1', 'sg2', 'sg3']
        self.conn.get({'Action': 'DescribeSecurityGroups'},
                      paginated=True).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual(expected_result,
                         self.conn.get_security_group_ids())
        self.mox.VerifyAll()


class CreateSecurityGroupTest(EcsConnectionTest):

    def testSuccess(self):
        get_response = {
            'SecurityGroupId': 'sg1'
        }
        self.conn.get({'Action': 'CreateSecurityGroup',
                       'Description': 'd'}).AndReturn(get_response)

        self.mox.ReplayAll()
        self.assertEqual('sg1',
                         self.conn.create_security_group('d'))
        self.mox.VerifyAll()


class GetSecurityGroupTest(EcsConnectionTest):

    def testSuccess(self):
        get_response1 = {
            'RegionId': 'r',
            'SecurityGroupId': 'sg',
            'Description': 'd',
            'Permissions': {'Permission': [
                {
                    'IpProtocol': 'TCP',
                    'PortRange': '22/22',
                    'SourceCidrIp': '2.2.2.2/32',
                    'Policy': 'Accept',
                    'NicType': 'internet'
                },
                {
                    'IpProtocol': 'TCP',
                    'PortRange': '22/22',
                    'SourceCidrIp': '1.1.1.1/32',
                    'Policy': 'Reject',
                    'NicType': 'internet'
                }]}
        }
        get_response2 = {
            'RegionId': 'r',
            'SecurityGroupId': 'sg',
            'Description': 'd',
            'Permissions': {'Permission': [
                {
                    'IpProtocol': 'TCP',
                    'PortRange': '22/22',
                    'SourceGroupId': 'sg2',
                    'Policy': 'Accept',
                    'NicType': 'intranet'
                },
                {
                    'IpProtocol': 'TCP',
                    'PortRange': '22/22',
                    'SourceCidrIp': '3.3.3.3/32',
                    'Policy': 'Reject',
                    'NicType': 'intranet'
                }]}
        }
        p1 = SecurityGroupPermission('TCP', '22/22', '2.2.2.2/32', None,
                                     'Accept', 'internet')
        p2 = SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                     'Reject', 'internet')
        p3 = SecurityGroupPermission('TCP', '22/22', None, 'sg2',
                                     'Accept', 'intranet')
        p4 = SecurityGroupPermission('TCP', '22/22', '3.3.3.3/32', None,
                                     'Reject', 'intranet')
        self.conn.get({'Action': 'DescribeSecurityGroupAttribute',
                       'SecurityGroupId': 'sg',
                       'NicType': 'internet'}).AndReturn(get_response1)
        self.conn.get({'Action': 'DescribeSecurityGroupAttribute',
                       'SecurityGroupId': 'sg',
                       'NicType': 'intranet'}).AndReturn(get_response2)

        self.mox.ReplayAll()
        self.assertEqual(SecurityGroup('r', 'sg', 'd', [p1, p2, p3, p4]),
                         self.conn.get_security_group('sg'))
        self.mox.VerifyAll()


class DeleteSecurityGroupTest(EcsConnectionTest):

    def testSuccess(self):
        self.conn.get({'Action': 'DeleteSecurityGroup',
                       'SecurityGroupId': 'sg'})

        self.mox.ReplayAll()
        self.conn.delete_security_group('sg')
        self.mox.VerifyAll()


class AddSecurityRuleTest(EcsConnectionTest):

    def testExternalCidrIp(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'internet'})

        self.mox.ReplayAll()
        self.conn.add_external_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32')
        self.mox.VerifyAll()

    def testExternalCidrIpWithPolicy(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'internet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.add_external_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32', policy='Reject')
        self.mox.VerifyAll()

    def testInternalCidrIp(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'intranet'})

        self.mox.ReplayAll()
        self.conn.add_internal_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32')
        self.mox.VerifyAll()

    def testInternalCidrIpWithPolicy(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'intranet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.add_internal_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32', policy='Reject')
        self.mox.VerifyAll()

    def testSourceSecurityGroup(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceGroupId': 'sg2',
                       'NicType': 'intranet'})

        self.mox.ReplayAll()
        self.conn.add_group_rule('sg', 'TCP', '22/22', 'sg2')
        self.mox.VerifyAll()

    def testSourceSecurityGroupWithPolicy(self):
        self.conn.get({'Action': 'AuthorizeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceGroupId': 'sg2',
                       'NicType': 'intranet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.add_group_rule('sg', 'TCP', '22/22', 'sg2',
                                 policy='Reject')
        self.mox.VerifyAll()


class RemoveSecurityRuleTest(EcsConnectionTest):

    def testExternalCidrIp(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'internet'})

        self.mox.ReplayAll()
        self.conn.remove_external_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32')
        self.mox.VerifyAll()

    def testExternalCidrIpWithPolicy(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'internet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.remove_external_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32', policy='Reject')
        self.mox.VerifyAll()

    def testInternalCidrIp(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'intranet'})

        self.mox.ReplayAll()
        self.conn.remove_internal_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32')
        self.mox.VerifyAll()

    def testInternalCidrIpWithPolicy(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceCidrIp': '1.1.1.1/32',
                       'NicType': 'intranet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.remove_internal_cidr_ip_rule(
            'sg', 'TCP', '22/22', '1.1.1.1/32', policy='Reject')
        self.mox.VerifyAll()

    def testSourceSecurityGroup(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceGroupId': 'sg2',
                       'NicType': 'intranet'})

        self.mox.ReplayAll()
        self.conn.remove_group_rule('sg', 'TCP', '22/22', 'sg2')
        self.mox.VerifyAll()

    def testSourceSecurityGroupWithPolicy(self):
        self.conn.get({'Action': 'RevokeSecurityGroup',
                       'SecurityGroupId': 'sg',
                       'IpProtocol': 'TCP',
                       'PortRange': '22/22',
                       'SourceGroupId': 'sg2',
                       'NicType': 'intranet',
                       'Policy': 'Reject'})

        self.mox.ReplayAll()
        self.conn.remove_group_rule('sg', 'TCP', '22/22', 'sg2',
                                    policy='Reject')
        self.mox.VerifyAll()


if __name__ == '__main__':
    unittest.main()
