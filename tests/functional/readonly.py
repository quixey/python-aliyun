#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2014, Quixey Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in self.c.mpliance with the License. You may obtain a copy of
# the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import aliyun.ecs.connection
import aliyun.slb.connection
import aliyun.ess.connection
import aliyun.ess.model
import unittest

class EcsReadOnlyTest(unittest.TestCase):

    def setUp(self):
        self.c = aliyun.ecs.connection.EcsConnection('cn-hangzhou')

    def testRegions(self):
        regions = self.c.get_all_regions()
        regionids = self.c.get_all_region_ids()
        self.assertEqual([r.region_id for r in regions], regionids)

    def testZones(self):
        zones = self.c.get_all_zones()
        zoneids = self.c.get_all_zone_ids()
        self.assertEqual([z.zone_id for z in zones], zoneids)

    def testClusters(self):
        clusters = self.c.get_all_clusters()
        self.assertTrue(len(clusters)>0)

    def testInstances(self):
        instances = self.c.get_all_instance_status()
        instanceids = self.c.get_all_instance_ids()
        self.assertEqual([i.instance_id for i in instances], instanceids)
        inst = self.c.get_instance(instanceids.pop())
        self.assertTrue(inst is not None)

    def testDescribeDisks(self):
        disks = self.c.describe_disks()
        self.assertTrue(len(disks)>0)

    def testDescribeSnapshots(self):
        iid = self.c.get_all_instance_ids().pop()
        disk = self.c.describe_instance_disks(iid).pop()
        snaps = self.c.describe_snapshots(iid, disk)
        if len(snaps)>0:
            snap = self.c.describe_snapshot(snaps.pop())
            self.assertTrue(snap is not None)

    def testDescribeImages(self):
        imgs = self.c.describe_images()
        self.assertTrue(len(imgs)>0)

    def testSecurityGroups(self):
        groups = self.c.describe_security_groups()
        gids = self.c.get_security_group_ids()
        self.assertEqual([g.security_group_id for g in groups], gids)
        group = self.c.get_security_group(gids.pop())
        self.assertTrue(group is not None)

    def testAutoSnapshotPolicy(self):
        print self.c.describe_auto_snapshot_policy()

class EssReadOnlyTests(unittest.TestCase):

    def setUp(self):
        self.con = aliyun.ess.connection('cn-qingdao')
    
    def describeGroupsTest(self):
        groups = self.con.describe_scaling_groups()
        self.assertTrue(isinstance(groups, list))
        if len(groups) > 0:
            self.assertTrue(isinstance(groups[0], aliyun.ess.model.ScalingGroup))

if __name__ == '__main__':
    unittests.main()
