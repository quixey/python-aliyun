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

import aliyun.slb.connection as slb
import unittest
from aliyun.slb.model import (
    BackendServer,
    BackendServerStatus,
    HTTPListener,
    LoadBalancer,
    LoadBalancerStatus,
    Listener,
    ListenerStatus,
    Region,
    TCPListener
)


class SlbRegionTest(unittest.TestCase):

    def testRegionEqual(self):
        r1 = Region('id1')
        r2 = Region('id1')
        self.assertEqual(r1, r2)

    def testRegionNotEqual(self):
        r1 = Region('id1')
        r2 = Region('id2')
        self.assertNotEqual(r1, r2)

    def testRegionRepr(self):
        r = Region('id')
        self.assertTrue(repr(r).startswith('<SLBRegion id at'))


class SlbLoadBalancerStatusTest(unittest.TestCase):

    def testLoadBalancerStatusEqual(self):
        lbs1 = LoadBalancerStatus('id1', 'name1', 'status1')
        lbs2 = LoadBalancerStatus('id1', 'name1', 'status1')
        self.assertEqual(lbs1, lbs2)

    def testLoadBalancerStatusNotEqual(self):
        lb1 = LoadBalancerStatus('id1', 'name1', 'status1')
        lb2 = LoadBalancerStatus('id2', 'name2', 'status2')
        self.assertNotEqual(lb1, lb2)

    def testLoadBalancerStatusIDNotEqual(self):
        lb1 = LoadBalancerStatus('id1', 'name1', 'status1')
        lb2 = LoadBalancerStatus('id2', 'name1', 'status1')
        self.assertNotEqual(lb1, lb2)

    def testLoadBalancerStatusNameNotEqual(self):
        lb1 = LoadBalancerStatus('id1', 'name1', 'status1')
        lb2 = LoadBalancerStatus('id1', 'name2', 'status1')
        self.assertNotEqual(lb1, lb2)

    def testLoadBalancerStatusStatusNotEqual(self):
        lb1 = LoadBalancerStatus('id1', 'name1', 'status1')
        lb2 = LoadBalancerStatus('id1', 'name1', 'status2')
        self.assertNotEqual(lb1, lb2)

    def testLoadBalancerStatusRepr(self):
        lb1 = LoadBalancerStatus('id', 'name', 'status')
        self.assertTrue(
            repr(lb1).startswith('<LoadBalancerStatus id is status at'))


class SlbLoadBalancerTest(unittest.TestCase):

    def testNoLoadBalancerId(self):
        try:
            LoadBalancer(
                None,
                'region',
                'name',
                'status',
                'ip',
                True,
                [1, 2],
                ['bs1', 'bs2'])  # BackendServers are not validated
            self.fail('Error expected without load balancer id')
        except slb.Error as err:
            self.assertTrue('requires load_balancer_id' in str(err))

    def testLBEqual(self):
        lb1 = LoadBalancer(
            'id',
            'region',
            'name',
            'status',
            'ip',
            True,
            [1,
             2])
        lb2 = LoadBalancer(
            'id',
            'region',
            'name',
            'status',
            'ip',
            True,
            [1,
             2])
        self.assertEqual(lb1, lb2)

    def testLBNotEqual(self):
        lb1 = LoadBalancer(
            'id',
            'region',
            'name',
            'status',
            'ip',
            True,
            [1,
             2])
        lb2 = LoadBalancer(
            'id',
            'region',
            'name2',
            'status',
            'ip',
            True,
            [1,
             2])
        self.assertNotEqual(lb1, lb2)

    def testRepr(self):
        lb = LoadBalancer(
            'id',
            'region',
            'name',
            'status',
            'ip',
            True,
            [1,
             2])
        self.assertTrue(repr(lb).startswith('<LoadBalancer id (name) at'))


class BackendServerTest(unittest.TestCase):

    def testEqual(self):
        bs1 = BackendServer('id', 1)
        bs2 = BackendServer('id', 1)
        self.assertEqual(bs1, bs2)

    def testNotEqual(self):
        bs1 = BackendServer('id', 1)
        bs2 = BackendServer('id2', 1)
        self.assertNotEqual(bs1, bs2)

    def testRepr(self):
        bs = BackendServer('id', 1)
        self.assertTrue(repr(bs).startswith(u'<BackendServer id'))


class ListenerStatusTest(unittest.TestCase):

    def testEqual(self):
        bs1 = BackendServer('id1', 1)
        bs2 = BackendServer('id2', 1)
        ls1 = ListenerStatus(1, [bs1, bs2])
        ls2 = ListenerStatus(1, [bs1, bs2])
        self.assertEqual(ls1, ls2)

    def testPortNotEqual(self):
        bs1 = BackendServer('id1', 1)
        bs2 = BackendServer('id2', 1)
        ls1 = ListenerStatus(1, [bs1, bs2])
        ls2 = ListenerStatus(2, [bs1, bs2])
        self.assertNotEqual(ls1, ls2)

    def testBackendsNotEqual(self):
        bs1 = BackendServer('id1', 1)
        bs2 = BackendServer('id2', 1)
        bs3 = BackendServer('id3', 1)
        bs4 = BackendServer('id4', 1)
        ls1 = ListenerStatus(1, [bs1, bs2])
        ls2 = ListenerStatus(1, [bs3, bs4])
        self.assertNotEqual(ls1, ls2)

    def testListenerStatusRepr(self):
        ls = ListenerStatus(1, [])
        self.assertTrue(repr(ls).startswith(u'<ListenerStatus 1 at '))


class TCPListenerTest(unittest.TestCase):

    def testEqual(self):
        l1 = TCPListener('id', 1, 1)
        l2 = TCPListener('id', 1, 1)
        self.assertEqual(l1, l2)

    def testNotEqual(self):
        l1 = TCPListener('id', 1, 1)
        l2 = TCPListener('id', 1, 2)
        self.assertNotEqual(l1, l2)

    def testRepr(self):
        listener = TCPListener('id', 1, 1)
        self.assertTrue(repr(listener).startswith(u'<TCPListener on 1 for id'))


class HTTPListenerTest(unittest.TestCase):

    def testEqual(self):
        l1 = HTTPListener('id', 1, 1)
        l2 = HTTPListener('id', 1, 1)
        self.assertEqual(l1, l2)

    def testNotEqual(self):
        l1 = HTTPListener('id', 1, 1)
        l2 = HTTPListener('id', 1, 2)
        self.assertNotEqual(l1, l2)

    def testStickyMismatch(self):
        try:
            lstn = HTTPListener('id', 1, 1, sticky_session=True)
            self.fail("sticky_session mismatches sticky_session_type.")
        except slb.Error as e:
            self.assertTrue('sticky_session_type must be specified' in str(e))

    def testStickyServerCookie(self):
        try:
            lstn = HTTPListener('id', 1, 1,
                                    sticky_session=True,
                                    sticky_session_type='server')
            self.fail(
                'cookie must be specified when using '
                'sticky_session_type="server"')
        except slb.Error as e:
            self.assertTrue(
                'cookie must be specified when using '
                'sticky_session_type' in str(e))

    def testRepr(self):
        lstn = HTTPListener('id', 1, 1)
        self.assertTrue(repr(lstn).startswith(u'<HTTPListener on 1 at '))


class BackendServerStatusTest(unittest.TestCase):

    def testEqual(self):
        bss1 = BackendServerStatus('id', 's')
        bss2 = BackendServerStatus('id', 's')
        self.assertEqual(bss1, bss2)

    def testNotEqual(self):
        bss1 = BackendServerStatus('id1', 's')
        bss2 = BackendServerStatus('id2', 's')
        self.assertNotEqual(bss1, bss2)

    def testRepr(self):
        bss = BackendServerStatus('id', 's')
        self.assertTrue(
            repr(bss).startswith(u'<BackendServerStatus id is s at '))

