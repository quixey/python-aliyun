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

import mox
import unittest

from aliyun.slb import connection as slb


class SlbConnectionTest(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        self.conn = slb.SlbConnection(
            'r',
            access_key_id='a',
            secret_access_key='s')
        self.mox.StubOutWithMock(self.conn, 'get')

    def tearDown(self):
        self.mox.UnsetStubs()


class RegionsTest(SlbConnectionTest):

    def testSuccess(self):
        get_response = {
            'Regions': {
                'Region': [
                    {'RegionId': 'r1'},
                    {'RegionId': 'r2'}
                ]
            }
        }
        expected_result = [slb.Region('r1'), slb.Region('r2')]
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


class GetLoadBalancerStatusTest(SlbConnectionTest):

    def testSuccess(self):
        get_response = {
            'LoadBalancers': {
                'LoadBalancer': [
                    {'LoadBalancerId': 'id1',
                     'LoadBalancerName': 'name1',
                     'LoadBalancerStatus': 'status1'},
                    {'LoadBalancerId': 'id2',
                     'LoadBalancerName': 'name2',
                     'LoadBalancerStatus': 'status2'}
                ]}
        }

        expected_result = [slb.LoadBalancerStatus('id1', 'name1', 'status1'),
                           slb.LoadBalancerStatus('id2', 'name2', 'status2')]
        self.conn.get({'Action': 'DescribeLoadBalancers'}
                      ).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual(
            expected_result,
            self.conn.get_all_load_balancer_status())
        self.mox.VerifyAll()

    def testWithInstance(self):
        get_response = {
            'LoadBalancers': {
                'LoadBalancer': [
                    {'LoadBalancerId': 'id1',
                     'LoadBalancerName': 'name1',
                     'LoadBalancerStatus': 'status1'}
                ]}
        }
        expected_result = [slb.LoadBalancerStatus('id1', 'name1', 'status1')]
        self.conn.get({'Action': 'DescribeLoadBalancers',
                       'ServerId': 'server_id'}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual(
            expected_result,
            self.conn.get_all_load_balancer_status('server_id'))
        self.mox.VerifyAll()

    def testGetIds(self):
        get_response = {
            'LoadBalancers': {
                'LoadBalancer': [
                    {'LoadBalancerId': 'id',
                     'LoadBalancerName': 'name',
                     'LoadBalancerStatus': 'status'}
                ]}
        }
        expected_result = ['id']
        self.conn.get({'Action': 'DescribeLoadBalancers'}
                      ).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual(
            expected_result,
            self.conn.get_all_load_balancer_ids())
        self.mox.VerifyAll()


class TestLoadBalancer(SlbConnectionTest):

    def testGetEqual(self):
        get_response = {
            'Address': 'a',
            'BackendServers': {
                'BackendServer': []
            },
            'AddressType': 'i',
            'ListenerPorts': {
                'ListenerPort': [1]
            },
            'LoadBalancerId': 'id',
            'LoadBalancerName': 'n',
            'LoadBalancerStatus': 's',
            'RegionId': 'r'
        }
        expect = slb.LoadBalancer('id', 'r', 'n', 's', 'a', 'i', [1])
        self.conn.get({'Action': 'DescribeLoadBalancerAttribute',
                       'LoadBalancerId': 'id'}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual(expect, self.conn.get_load_balancer('id'))
        self.mox.VerifyAll()

    def testGetManyBackends(self):
        get_response = {
            'Address': 'a',
            'BackendServers': {
                'BackendServer': [
                    {'ServerId': 'sid1', 'Weight': 1},
                    {'ServerId': 'sid2', 'Weight': 1},
                ]},
            'AddressType': 'i',
            'ListenerPorts': {
                'ListenerPort': [1]
            },
            'LoadBalancerId': 'id',
            'LoadBalancerName': 'n',
            'LoadBalancerStatus': 's',
            'RegionId': 'r'
        }
        expected_backends = [
            slb.BackendServer('sid1', 1),
            slb.BackendServer('sid2', 1),
        ]
        expect = slb.LoadBalancer(
            'id',
            'r',
            'n',
            's',
            'a',
            'i',
            [1],
            expected_backends)
        self.conn.get({'Action': 'DescribeLoadBalancerAttribute',
                       'LoadBalancerId': 'id'}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual(expect, self.conn.get_load_balancer('id'))
        self.mox.VerifyAll()

    def testCreateMinimal(self):
        get_response = {'Address': 'address',
                        'LoadBalancerId': 'id',
                        'LoadBalancerName': 'name'}
        self.conn.get({'Action': 'CreateLoadBalancer',
                       'RegionId': 'r'}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.assertEqual('id', self.conn.create_load_balancer('r'))
        self.mox.VerifyAll()

    def testCreateFull(self):
        get_response = {'Address': 'a',
                        'LoadBalancerId': 'id',
                        'AddressType': 'i',
                        'InternetChargeType': 'pbbw',
                        'Bandwidth': 1000,
                        'LoadBalancerName': 'n'}
        self.conn.get({'Action': 'CreateLoadBalancer',
                       'LoadBalancerName': 'n',
                       'AddressType': 'i',
                       'InternetChargeType': 'pbbw',
                       'Bandwidth': 1000,
                       'RegionId': 'r'}).AndReturn(get_response)
        self.mox.ReplayAll()
        lb = self.conn.create_load_balancer(region_id='r',
                                            load_balancer_name='n',
                                            address_type='i',
                                            internet_charge_type='pbbw',
                                            bandwidth=1000)
        self.assertEqual('id', lb)
        self.mox.VerifyAll()

    def testDeleteLoadBalancer(self):
        get_response = {'RequestId': 'r'}
        self.conn.get({'Action': 'DeleteLoadBalancer',
                       'LoadBalancerId': 'i'}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.conn.delete_load_balancer('i')
        self.mox.VerifyAll()

    def testStartLoadBalancerListener(self):
        get_response = {'RequestId': 'r'}
        self.conn.get({'Action': 'StartLoadBalancerListener',
                       'LoadBalancerId': 'i',
                       'ListenerPort': 1}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.conn.start_load_balancer_listener('i', 1)
        self.mox.VerifyAll()

    def testStopLoadBalancerListener(self):
        get_response = {'RequestId': 'r'}
        self.conn.get({'Action': 'StopLoadBalancerListener',
                       'LoadBalancerId': 'i',
                       'ListenerPort': 1}).AndReturn(get_response)
        self.mox.ReplayAll()
        self.conn.stop_load_balancer_listener('i', 1)
        self.mox.VerifyAll()

    def testSetStatus(self):
        self.conn.get({'Action': 'SetLoadBalancerStatus',
                       'LoadBalancerId': 'id',
                       'LoadBalancerStatus': 'status'}).AndReturn({})
        self.mox.ReplayAll()
        self.conn.set_load_balancer_status('id', 'status')
        self.mox.VerifyAll()

    def testSetName(self):
        self.conn.get({'Action': 'SetLoadBalancerName',
                       'LoadBalancerId': 'id',
                       'LoadBalancerName': 'name'}).AndReturn({})
        self.mox.ReplayAll()
        self.conn.set_load_balancer_name('id', 'name')
        self.mox.VerifyAll()


class TestListeners(SlbConnectionTest):

    def testDelete(self):
        self.conn.get({'Action': 'DeleteLoadBalancerListener',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1}).AndReturn({})
        self.mox.ReplayAll()
        self.conn.delete_listener('id', 1)
        self.mox.VerifyAll()

    def testSetStatus(self):
        self.conn.get({'Action': 'SetLoadBalancerListenerStatus',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1,
                       'ListenerStatus': 'status'}).AndReturn({})
        self.mox.ReplayAll()
        self.conn.set_listener_status('id', 1, 'status')
        self.mox.VerifyAll()


class TestTCPListener(SlbConnectionTest):

    def testEqual(self):
        response = {
            'BackendServerPort': 1001,
            'ConnectTimeout': 5,
            'HealthCheck': 'off',
            'Interval': 2,
            'ListenerPort': 1000,
            'PersistenceTimeout': 0,
            'RequestId': 'rid',
            'Scheduler': 'wrr',
            'Status': 'stopped'
        }

        self.conn.get({'Action': 'DescribeLoadBalancerTCPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1000}).AndReturn(response)
        self.mox.ReplayAll()
        listener1 = self.conn.get_tcp_listener('id', 1000)
        expected = slb.TCPListener('id', 1000, 1001, 'stopped')
        self.assertEqual(listener1, expected)
        self.mox.VerifyAll()

    def testCreateMinimal(self):
        self.conn.get({'Action': 'CreateLoadBalancerTCPListener',
                       'LoadBalancerId': 'id',
                       'HealthyThreshold': 3,
                       'UnhealthyThreshold': 3,
                       'ListenerPort': 1,
                       'BackendServerPort': 1})
        self.mox.ReplayAll()
        self.conn.create_tcp_listener('id', 1, 1)
        self.mox.VerifyAll()

    def testCreateFull(self):
        self.conn.get({'Action': 'CreateLoadBalancerTCPListener',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1,
                       'BackendServerPort': 2,
                       'HealthyThreshold': 3,
                       'UnhealthyThreshold': 4,
                       'ListenerStatus': 'status',
                       'Scheduler': 'scheduler',
                       'HealthCheck': 'on',
                       'ConnectTimeout': 5,
                       'Interval': 6,
                       'ConnectPort': 7,
                       'PersistenceTimeout': 8
                       })
        self.mox.ReplayAll()
        self.conn.create_tcp_listener(
            'id', 1, 2, 3, 4, 'status', 'scheduler', True, 5, 6, 7, 8)
        self.mox.VerifyAll()

    def testUpdateMinimal(self):
        self.conn.get({'Action': 'SetLoadBalancerTCPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1})
        self.mox.ReplayAll()
        self.conn.update_tcp_listener('id', 1)
        self.mox.VerifyAll()

    def testUpdateFull(self):
        self.conn.get({'Action': 'SetLoadBalancerTCPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1,
                       'HealthyThreshold': 2,
                       'UnhealthyThreshold': 3,
                       'Scheduler': 'scheduler',
                       'HealthCheck': 'on',
                       'ConnectTimeout': 4,
                       'Interval': 5,
                       'ConnectPort': 6,
                       'PersistenceTimeout': 7
                       })
        self.mox.ReplayAll()
        self.conn.update_tcp_listener('id', 1,
                healthy_threshold=2,
                unhealthy_threshold=3,
                scheduler='scheduler',
                health_check=True,
                connect_timeout=4,
                interval=5,
                connect_port=6,
                persistence_timeout=7)
        self.mox.VerifyAll()


class TestHTTPListener(SlbConnectionTest):

    def testEqual(self):
        response = {
            'BackendServerPort': 1,
            'Cookie': '',
            'Domain': '',
            'HealthCheck': 'off',
            'ListenerPort': 1,
            'Scheduler': 'wrr',
            'Status': 'stopped',
            'StickySession': 'off',
            'StickySessionapiType': '',
            'URI': '',
            'XForwardedFor': 'off'
        }

        self.conn.get({'Action': 'DescribeLoadBalancerHTTPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1}).AndReturn(response)
        self.mox.ReplayAll()
        listener1 = self.conn.get_http_listener('id', 1)
        expected = slb.HTTPListener('id', 1, 1, 'stopped')
        self.assertEqual(listener1, expected)
        self.mox.VerifyAll()

    def testCreateMinimal(self):
        self.conn.get({'Action': 'CreateLoadBalancerTCPListener',
                       'LoadBalancerId': 'id',
                       'HealthyThreshold': 3,
                       'UnhealthyThreshold': 3,
                       'ListenerPort': 1,
                       'BackendServerPort': 1})
        self.mox.ReplayAll()
        self.conn.create_tcp_listener('id', 1, 1)
        self.mox.VerifyAll()

    def testCreateFull(self):
        self.conn.get({'Action': 'CreateLoadBalancerHTTPListener',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1,
                       'BackendServerPort': 2,
                       'HealthyThreshold': 3,
                       'UnhealthyThreshold': 4,
                       'ConnectTimeout': 5,
                       'Interval': 6,
                       'Bandwidth': 8,
                       'Scheduler': 'schedule',
                       'HealthCheck': 'on',
                       'XForwardedFor': 'on',
                       'StickySession': 'on',
                       'StickySessionapiType': 'server',
                       'CookieTimeout': 7,
                       'Cookie': 'cookie',
                       'Domain': 'domain',
                       'URI': 'uri',
                       })
        self.mox.ReplayAll()
        self.conn.create_http_listener(
            load_balancer_id='id',
            listener_port=1,
            backend_server_port=2,
            bandwidth='8',
            sticky_session='on',
            health_check='on',
            healthy_threshold=3,
            unhealthy_threshold=4,
            scheduler='schedule',
            connect_timeout=5,
            interval=6,
            x_forwarded_for=True,
            sticky_session_type='server',
            cookie_timeout=7,
            cookie='cookie',
            domain='domain',
            uri='uri')
        self.mox.VerifyAll()

    def testUpdateMinimal(self):
        self.conn.get({'Action': 'SetLoadBalancerHTTPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1})
        self.mox.ReplayAll()
        self.conn.update_http_listener('id', 1)
        self.mox.VerifyAll()

    def testUpdateFull(self):
        self.conn.get({'Action': 'SetLoadBalancerHTTPListenerAttribute',
                       'LoadBalancerId': 'id',
                       'ListenerPort': 1,
                       'HealthyThreshold': 2,
                       'UnhealthyThreshold': 3,
                       'Scheduler': 'schedule',
                       'HealthCheck': 'on',
                       'HealthCheckTimeout': 4,
                       'Interval': 5,
                       'XForwardedFor': 'on',
                       'StickySession': 'on',
                       'StickySessionapiType': 'server',
                       'CookieTimeout': 6,
                       'Cookie': 'cookie',
                       'Domain': 'domain',
                       'URI': 'uri',
                       })
        self.mox.ReplayAll()
        self.conn.update_http_listener('id', 1,
                healthy_threshold=2,
                unhealthy_threshold=3,
                scheduler='schedule',
                health_check=True,
                health_check_timeout=4,
                interval=5,
                x_forwarded_for=True,
                sticky_session=True,
                sticky_session_type='server',
                cookie_timeout=6,
                cookie='cookie',
                domain='domain',
                uri='uri')
        self.mox.VerifyAll()


class TestBackendServers(SlbConnectionTest):

    def testBasicGet(self):
        response = {"Listeners": {"Listener": [
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status1",
                 "ServerId": "id1"},
            ]},
                "ListenerPort": 1
            },
        ]}}
        self.conn.get({'Action': 'DescribeBackendServers',
                       'LoadBalancerId': 'id'}).AndReturn(response)
        expected = [slb.ListenerStatus(
            1, [slb.BackendServerStatus('id1', 'status1')])]
        self.mox.ReplayAll()
        self.assertEqual(expected, self.conn.get_backend_servers('id'))
        self.mox.VerifyAll()

    def testGetWithListenerPort(self):
        response = {"Listeners": {"Listener": [
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status1",
                 "ServerId": "id1"},
            ]},
                "ListenerPort": 1
            },
        ]}}
        self.conn.get({'Action': 'DescribeBackendServers',
                       'ListenerPort': 1,
                       'LoadBalancerId': 'id'}).AndReturn(response)
        expected = [slb.ListenerStatus(
            1, [slb.BackendServerStatus('id1', 'status1')])]
        self.mox.ReplayAll()
        self.assertEqual(expected, self.conn.get_backend_servers('id', 1))
        self.mox.VerifyAll()

    def testGetMultiple(self):
        response = {"Listeners": {"Listener": [
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status1",
                 "ServerId": "id1"},
                {"ServerHealthStatus": "status2", "ServerId": "id2"}
            ]},
                "ListenerPort": 1
            },
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status3",
                 "ServerId": "id3"},
                {"ServerHealthStatus": "status4", "ServerId": "id4"}
            ]},
                "ListenerPort": 2
            },
        ]}}
        self.conn.get({'Action': 'DescribeBackendServers',
                       'LoadBalancerId': 'id'}).AndReturn(response)
        expected = [
            slb.ListenerStatus(1,
                               [slb.BackendServerStatus('id1', 'status1'),
                                slb.BackendServerStatus('id2', 'status2')]
                               ),
            slb.ListenerStatus(2,
                               [slb.BackendServerStatus('id3', 'status3'),
                                slb.BackendServerStatus('id4', 'status4')]
                               )]
        self.mox.ReplayAll()
        self.assertEqual(expected, self.conn.get_backend_servers('id'))
        self.mox.VerifyAll()

    def testGetMultipleIds(self):
        response = {"Listeners": {"Listener": [
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status1",
                 "ServerId": "id1"},
                {"ServerHealthStatus": "status2", "ServerId": "id2"}
            ]},
                "ListenerPort": 1
            },
            {"BackendServers": {"BackendServer": [
                {"ServerHealthStatus": "status3",
                 "ServerId": "id3"},
                {"ServerHealthStatus": "status4", "ServerId": "id4"}
            ]},
                "ListenerPort": 2
            },
        ]}}
        self.conn.get({'Action': 'DescribeBackendServers',
                       'LoadBalancerId': 'id'}).AndReturn(response)
        self.mox.ReplayAll()
        expected = ['id1', 'id2', 'id3', 'id4']
        self.assertEqual(
            set(expected),
            set(self.conn.get_backend_server_ids('id')))
        self.mox.VerifyAll()

    def testRemoveBackendServers(self):
        params = {'Action': 'RemoveBackendServers',
                  'LoadBalancerId': 'lbid',
                  'BackendServers': [{'ServerId': 'id1'}]
                  }
        self.conn.get(params)
        self.mox.ReplayAll()
        self.conn.remove_backend_servers('lbid', [slb.BackendServer('id1', 1)])
        self.mox.VerifyAll()

    def testRemoveBackendServerIds(self):
        params = {'Action': 'RemoveBackendServers',
                  'LoadBalancerId': 'lbid',
                  'BackendServers': [{'ServerId': 'id1'}]
                  }
        self.conn.get(params)
        self.mox.ReplayAll()
        self.conn.remove_backend_server_ids('lbid', ['id1'])
        self.mox.VerifyAll()

    def testAddBackendServers(self):
        params = {'Action': 'AddBackendServers',
                  'LoadBalancerId': 'lbid',
                  'BackendServers': [{'ServerId': 'id1', 'Weight': 1}]
                  }
        self.conn.get(params)
        self.mox.ReplayAll()
        self.conn.add_backend_servers('lbid', [slb.BackendServer('id1', 1)])
        self.mox.VerifyAll()

    def testAddBackendServerNullWeight(self):
        params = {'Action': 'AddBackendServers',
                  'LoadBalancerId': 'lbid',
                  'BackendServers': [{'ServerId': 'id1'}]
                  }
        self.conn.get(params)
        self.mox.ReplayAll()
        self.conn.add_backend_servers('lbid', [slb.BackendServer('id1', None)])
        self.mox.VerifyAll()

    def testAddBackendServerIds(self):
        params = {'Action': 'AddBackendServers',
                  'LoadBalancerId': 'lbid',
                  'BackendServers': [{'ServerId': 'id1'}]
                  }
        self.conn.get(params)
        self.mox.ReplayAll()
        self.conn.add_backend_server_ids('lbid', ['id1'])
        self.mox.VerifyAll()


class TestDeregister(SlbConnectionTest):

    def testDeregisterSimple(self):
        lb_request = {'Action': 'DescribeLoadBalancers', 'ServerId': 'sid'}
        lb_resp = {'LoadBalancers': {'LoadBalancer': [{
            'LoadBalancerId': 'lbid',
            'LoadBalancerName': 'lbname',
            'LoadBalancerStatus': 'lbstatus'}]}}

        bs_request = {
            'Action': 'RemoveBackendServers', 'LoadBalancerId': 'lbid',
            'BackendServers': [{'ServerId': 'sid'}]
        }
        self.conn.get(lb_request).MultipleTimes().AndReturn(lb_resp)
        self.conn.get(bs_request).MultipleTimes()
        self.mox.ReplayAll()
        lbs = self.conn.deregister_backend_server_ids(['sid', 'sid'])
        self.assertEqual(lbs, ['lbid'])
        self.mox.VerifyAll()

    def testDeregisterBackendServers(self):
        lb_request = {'Action': 'DescribeLoadBalancers', 'ServerId': 'sid'}
        lb_resp = {'LoadBalancers': {'LoadBalancer': [{
            'LoadBalancerId': 'lbid',
            'LoadBalancerName': 'lbname',
            'LoadBalancerStatus': 'lbstatus'}]}}

        bs_request = {
            'Action': 'RemoveBackendServers', 'LoadBalancerId': 'lbid',
            'BackendServers': [{'ServerId': 'sid'}]
        }
        self.conn.get(lb_request).MultipleTimes().AndReturn(lb_resp)
        self.conn.get(bs_request).MultipleTimes()
        self.mox.ReplayAll()
        backends = [slb.BackendServer('sid', None), ]
        lbs = self.conn.deregister_backend_servers(backends)
        self.assertEqual(lbs, ['lbid'])
        self.mox.VerifyAll()


if __name__ == '__main__':
    unittest.main()
