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
import mox
import time
import unittest

from aliyun.ecs import connection as ecs


class RegionTest(unittest.TestCase):

    def testEqual(self):
        region1 = ecs.Region('regionid1', 'regionname1')
        region2 = ecs.Region('regionid1', 'regionname1')
        self.assertEqual(region1, region2)

    def testIDNotEqual(self):
        region1 = ecs.Region('regionid1', 'regionname1')
        region2 = ecs.Region('regionid2', 'regionname1')
        self.assertNotEqual(region1, region2)

    def testNameNotEqual(self):
        region1 = ecs.Region('regionid1', 'regionname1')
        region2 = ecs.Region('regionid1', 'regionname2')
        self.assertNotEqual(region1, region2)

    def testRepr(self):
        region = ecs.Region('region', 'name')
        self.assertTrue(repr(region).startswith(u'<Region region (name) at '))


class InstanceTest(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.instance1 = ecs.Instance(
            'id',
            'name',
            'imageId',
            'regionId',
            'instanceType',
            'hostname',
            'status',
            ['sg1', 'sg2'],
            ['ip1', 'ip2'],
            ['ip3', 'ip4'],
            'accounting',
            1, 1, self.now,
            'desc', 'cluster', [], 'z')

    def testEqual(self):
        instance2 = ecs.Instance(
            'id',
            'name',
            'imageId',
            'regionId',
            'instanceType',
            'hostname',
            'status',
            ['sg1', 'sg2'],
            ['ip1', 'ip2'],
            ['ip3', 'ip4'],
            'accounting',
            1, 1, self.now,
            'desc', 'cluster', [], 'z')

        self.assertEqual(self.instance1, instance2)

    def testNotEqual(self):
        instance2 = ecs.Instance(
            'id',
            'name',
            'imageId',
            'regionId',
            'instanceType',
            'hostname2',
            'status',
            ['sg1', 'sg2'],
            ['ip1', 'ip2'],
            ['ip3', 'ip4'],
            'accounting',
            1, 1, self.now,
            'desc', 'cluster', [], 'z')

        self.assertNotEqual(self.instance1, instance2)

    def testRepr(self):
        self.assertTrue(repr(self.instance1).startswith('<Instance id at'))


class InstanceStatusTest(unittest.TestCase):

    def testEqual(self):
        is1 = ecs.InstanceStatus('i1', 'running')
        is2 = ecs.InstanceStatus('i1', 'running')
        self.assertEqual(is1, is2)

    def testNotEqual(self):
        is1 = ecs.InstanceStatus('i1', 'running')
        is2 = ecs.InstanceStatus('i1', 'stopped')
        self.assertNotEqual(is1, is2)

    def testRepr(self):
        is1 = ecs.InstanceStatus('i1', 'running')
        self.assertTrue(repr(is1).startswith(u'<InstanceId i1 is running at'))


class InstanceTypeTest(unittest.TestCase):

    def testEqual(self):
        t1 = ecs.InstanceType('t1', 4, 2)
        t2 = ecs.InstanceType('t1', 4, 2)
        self.assertEqual(t1, t2)

    def testNotEqual(self):
        t1 = ecs.InstanceType('t1', 4, 2)
        t2 = ecs.InstanceType('t1', 4, 3)
        self.assertNotEqual(t1, t2)

    def testRepr(self):
        t1 = ecs.InstanceType('t1', 4, 2)
        self.assertTrue(repr(t1).startswith(u'<InstanceType t1'))


class SnapshotTest(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()

    def testEqual(self):
        s1 = ecs.Snapshot('s1', 'sn', 100, self.now)
        s2 = ecs.Snapshot('s1', 'sn', 100, self.now)
        self.assertEqual(s1, s2)

    def testNotEqual(self):
        s1 = ecs.Snapshot('s1', 'sn', 100, self.now)
        s2 = ecs.Snapshot('s1', 'sn', 99, self.now)
        self.assertNotEqual(s1, s2)

    def testRepr(self):
        s1 = ecs.Snapshot('s1', 'sn', 100, self.now)
        self.assertTrue(repr(s1).startswith(u'<Snapshot s1 is 100% ready at'))


class DiskTest(unittest.TestCase):

    def testEqual(self):
        d1 = ecs.Disk('d1', 'system', 'cloud', 5)
        d2 = ecs.Disk('d1', 'system', 'cloud', 5)
        self.assertEqual(d1, d2)

    def testNotEqual(self):
        d1 = ecs.Disk('d1', 'system', 'cloud', 5)
        d2 = ecs.Disk('d1', 'system', 'cloud', 6)
        self.assertNotEqual(d1, d2)

    def testRepr(self):
        d1 = ecs.Disk('d1', 'system', 'cloud', 5)
        self.assertTrue(
            repr(d1).startswith(u'<Disk d1 of type system is 5GB at'))


class ImageTest(unittest.TestCase):

    def testEqual(self):
        i1 = ecs.Image('i1', '1.0', 'ubuntu12.04', 'standard image', 20,
                       'i386', 'system', 'ubuntu', 'public')
        i2 = ecs.Image('i1', '1.0', 'ubuntu12.04', 'standard image', 20,
                       'i386', 'system', 'ubuntu', 'public')
        self.assertEqual(i1, i2)

    def testNotEqual(self):
        i1 = ecs.Image('i1', '1.0', 'ubuntu12.04', 'standard image', 20,
                       'i386', 'system', 'ubuntu', 'public')
        i2 = ecs.Image('i1', '1.0', 'ubuntu12.04', 'standard image', 21,
                       'i386', 'system', 'ubuntu', 'public')
        self.assertNotEqual(i1, i2)

    def testRepr(self):
        i1 = ecs.Image('i1', '1.0', 'ubuntu12.04', 'standard image', 20,
                       'i386', 'system', 'ubuntu', 'public')
        self.assertTrue(repr(i1).startswith(
            u'<Image i1(standard image) for platform ubuntu12.04 and arch i3'))


class SecurityGroupInfoTest(unittest.TestCase):

    def testEqual(self):
        sg1 = ecs.SecurityGroupInfo('sg1', 'desc')
        sg2 = ecs.SecurityGroupInfo('sg1', 'desc')
        self.assertEqual(sg1, sg2)

    def testNotEqual(self):
        sg1 = ecs.SecurityGroupInfo('sg1', 'desc')
        sg2 = ecs.SecurityGroupInfo('sg2', 'desc')
        self.assertNotEqual(sg1, sg2)

    def testRepr(self):
        sg1 = ecs.SecurityGroupInfo('sg1', 'desc1')
        self.assertTrue(repr(sg1).startswith(u'<SecurityGroupInfo sg1'))


class SecurityGroupPermission(unittest.TestCase):

    def testEqual(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        p2 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        self.assertEqual(p1, p2)

    def testNotEqual(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        p2 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Reject', 'internet')
        self.assertNotEqual(p1, p2)

    def testRepr(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        self.assertTrue(repr(p1).startswith(
            u'<SecurityGroupPermission Accept TCP 22/22 from 1.1.1.1/32 at'))


class SecurityGroupTest(unittest.TestCase):

    def testEqual(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        p2 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        sg1 = ecs.SecurityGroup('r', 'sg1', 'd', [p1])
        sg2 = ecs.SecurityGroup('r', 'sg1', 'd', [p2])
        self.assertEqual(sg1, sg2)

    def testNotEqual(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        p2 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Reject', 'internet')
        sg1 = ecs.SecurityGroup('r', 'sg1', 'd', [p1])
        sg2 = ecs.SecurityGroup('r', 'sg1', 'd', [p2])
        self.assertNotEqual(sg1, sg2)

    def testRepr(self):
        p1 = ecs.SecurityGroupPermission('TCP', '22/22', '1.1.1.1/32', None,
                                         'Accept', 'internet')
        sg1 = ecs.SecurityGroup('r', 'sg1', 'd', [p1])
        self.assertTrue(repr(sg1).startswith(
            u'<SecurityGroup sg1, d at'))

class ZoneTest(unittest.TestCase):

    def testEqualSimple(self):
        z1 = ecs.Zone('id1', 'name1')
        z2 = ecs.Zone('id1', 'name1')
        self.assertEqual(z1, z2)

    def testEqualFull(self):
        z1 = ecs.Zone('id1', 'name1', ['resource1'], ['disktype1'])
        z2 = ecs.Zone('id1', 'name1', ['resource1'], ['disktype1'])
        self.assertEqual(z1, z2)

    def testNotEqual(self):
        z1 = ecs.Zone('id1', 'name1')
        z2 = ecs.Zone('id2', 'name2')
        self.assertNotEqual(z1, z2)

    def testNotEqualDeep(self):
        z1 = ecs.Zone('id1', 'name1', ['resource1'], ['disktype1'])
        z2 = ecs.Zone('id1', 'name1', ['resource2'], ['disktype2'])
        self.assertNotEqual(z1, z2)

    def testRepr(self):
        z = ecs.Zone('id', 'name')
        self.assertTrue(repr(z).startswith('<Zone id (name) at'))

    def testDiskSupported(self):
        z1 = ecs.Zone('id', 'name', ['resource1'], ['disktype1'])
        self.assertTrue(z1.disk_supported('disktype1'))

    def testResourceCreationSupported(self):
        z1 = ecs.Zone('id', 'name', ['resource1'], ['disktype1'])
        self.assertTrue(z1.resource_creation_supported('resource1'))
