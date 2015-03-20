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

import collections
from aliyun import connection
from aliyun.slb.model import (
    BackendServer,
    BackendServerStatus,
    HTTPListener,
    LoadBalancer,
    LoadBalancerStatus,
    ListenerStatus,
    Region,
    TCPListener
)


class Error(Exception):

    """Base Exception class for this module."""


class SlbConnection(connection.Connection):

    """A connection to Aliyun SLB service."""

    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        """Constructor.

        If the access and secret key are not provided the credentials are
        looked for in $HOME/.aliyun.cfg or /etc/aliyun.cfg.

        Args:
            region_id (str): The id of the region to connect to.
            access_key_id (str): The access key id.
            secret_access_key (str): The secret access key.
        """
        super(SlbConnection, self).__init__(
            region_id, 'slb', access_key_id=access_key_id,
            secret_access_key=secret_access_key)

    def get_all_regions(self):
        """Get all regions.

        Return: list[slb.Region]
        """
        resp = self.get({'Action': 'DescribeRegions'})
        regions = []
        for region in resp['Regions']['Region']:
            regions.append(Region(region['RegionId']))
        return regions

    def get_all_region_ids(self):
        return [r.region_id for r in self.get_all_regions()]

    def get_all_load_balancer_status(self, instance_id=None):
        """Get all LoadBalancerStatus in the region.

        Args:
            instance_id (str, optional): Restrict results to LBs with this
                instance.

        Return:
            List of LoadBalancerStatus.
        """
        lb_status = []
        params = {'Action': 'DescribeLoadBalancers'}

        if instance_id:
            params['ServerId'] = instance_id

        resp = self.get(params)
        for lb in resp['LoadBalancers']['LoadBalancer']:
            new_lb_status = LoadBalancerStatus(lb['LoadBalancerId'],
                                               lb['LoadBalancerName'],
                                               lb['LoadBalancerStatus'])
            lb_status.append(new_lb_status)

        return lb_status

    def get_all_load_balancer_ids(self):
        """Get all the load balancer IDs in the region."""
        return (
            [x.load_balancer_id for x in self.get_all_load_balancer_status()]
        )

    def delete_load_balancer(self, load_balancer_id):
        """Delete a LoadBalancer by ID

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to delete.
        """
        params = {
            'Action': 'DeleteLoadBalancer',
            'LoadBalancerId': load_balancer_id
        }

        return self.get(params)

    def get_load_balancer(self, load_balancer_id):
        """Get a LoadBalancer by ID.

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.

        Returns:
            LoadBalancer with given ID.
        """
        resp = self.get({
            'Action': 'DescribeLoadBalancerAttribute',
            'LoadBalancerId': load_balancer_id
        })

        backend_servers = []
        for bs in resp['BackendServers']['BackendServer']:
            backend_servers.append(BackendServer(bs['ServerId'], bs['Weight']))

        return LoadBalancer(resp['LoadBalancerId'],
                            resp['RegionId'],
                            resp['LoadBalancerName'],
                            resp['LoadBalancerStatus'],
                            resp['Address'],
                            resp['AddressType'],
                            [port for port in resp['ListenerPorts']
                                ['ListenerPort']],
                            backend_servers)

    def create_load_balancer(self, region_id,
                             address_type=None,
                             internet_charge_type=None,
                             bandwidth=None,
                             load_balancer_name=None):
        """Create a load balancer. This does not configure listeners nor
        backend servers.

        Args:
            region_id (str): An id from get_all_region_ids()
            addres_type (str): IP the SLB on the public network ('internet',
                               default) or the private network ('intranet')
            internet_charge_type (str): 'paybytraffic' (default) vs
                                        'paybybandwidth'
            bandwidth (int): peak burst speed of 'paybybandwidth' type slbs.
                             Listener must be set first before this will take
                             effect. default: 1 (unit Mbps)
            load_balancer_name (str): Name of the SLB. 80 char max. Optional.
        Returns:
            load_balancer_id of the created LB. Address and Name are not given.
        """
        params = {
            'Action': 'CreateLoadBalancer',
            'RegionId': region_id
            }

        if load_balancer_name is not None:
            params['LoadBalancerName'] = load_balancer_name

        if address_type is not None:
            params['AddressType'] = address_type.lower()

        if internet_charge_type is not None:
            params['InternetChargeType'] = internet_charge_type.lower()

        if bandwidth is not None:
            params['Bandwidth'] = bandwidth

        resp = self.get(params)
        self.logging.debug("Created a load balancer: %(LoadBalancerId)s named %(LoadBalancerName)s at %(Address)s".format(resp))
        return resp['LoadBalancerId']

    def set_load_balancer_status(self, load_balancer_id, status):
        """Set the Status of an SLB

        Args:
            load_balancer_id (str): SLB ID
            status (str): One of 'inactive' or 'active'
        """
        params = {
            'Action': 'SetLoadBalancerStatus',
            'LoadBalancerId': load_balancer_id,
            'LoadBalancerStatus': status
        }
        return self.get(params)

    def set_load_balancer_name(self, load_balancer_id, name):
        """Set the Name of an SLB

        Args:
            load_balancer_id (str): SLB ID
            name (str): Alias for the SLB. Up to 64 characters.
        """
        params = {
            'Action': 'SetLoadBalancerName',
            'LoadBalancerId': load_balancer_id,
            'LoadBalancerName': name
        }
        return self.get(params)

    def delete_listener(self, load_balancer_id, listener_port):
        """Delete the SLB Listner on specified port

        Args:
            load_balancer_id (str): SLB ID
            listener_port (int): SLB Listener port. Between 1 and 65535.
        """
        params = {
            'Action': 'DeleteLoadBalancerListener',
            'LoadBalancerId': load_balancer_id,
            'ListenerPort': listener_port
        }
        return self.get(params)

    def set_listener_status(self, load_balancer_id, listener_port, status):
        """Set the status of an SLB Listener. Turn them on or off.

        Args:
            load_balancer_id (str): SLB ID
            listener_port (int): SLB Listener port. Between 1 and 65535.
            status (str): 'inactive' for off and 'active' for on.
        """
        params = {
            'Action': 'SetLoadBalancerListenerStatus',
            'LoadBalancerId': load_balancer_id,
            'ListenerPort': listener_port,
            'ListenerStatus': status
        }
        return self.get(params)

    def get_tcp_listener(self, load_balancer_id, listener_port):
        """Get the TCP Listener from an SLB ID and port

        Args:
            load_balancer_id (str): SLB ID
            listener_port (int): SLB Listener port. Between 1 and 65535.

        Returns:
            TCPListener
        """
        params = {
            'Action': 'DescribeLoadBalancerTCPListenerAttribute',
            'LoadBalancerId': load_balancer_id,
            'ListenerPort': listener_port
        }
        resp = self.get(params)

        if 'ConnectPort' not in resp:
            resp['ConnectPort'] = resp['BackendServerPort']

        return TCPListener(load_balancer_id,
                           int(resp['ListenerPort']),
                           int(resp['BackendServerPort']),
                           listener_status=resp['Status'],
                           scheduler=resp['Scheduler'] or None,
                           health_check=resp['HealthCheck'] == 'on',
                           connect_port=int(resp['ConnectPort']) or None,
                           persistence_timeout=int(resp['PersistenceTimeout']))

    def get_http_listener(self, load_balancer_id, listener_port):
        """Get the HTTP Listener from an SLB ID and port

        Args:
            load_balancer_id (str): SLB ID
            listener_port (int): SLB Listener port. Between 1 and 65535.

        Returns:
            HTTPListener
        """
        params = {
            'Action': 'DescribeLoadBalancerHTTPListenerAttribute',
            'LoadBalancerId': load_balancer_id,
            'ListenerPort': listener_port
        }
        resp = self.get(params)

        return HTTPListener(load_balancer_id,
                            int(resp['ListenerPort']),
                            int(resp['BackendServerPort']),
                            listener_status=resp['Status'] or None,
                            scheduler=resp['Scheduler'] or None,
                            health_check=resp['HealthCheck'] == 'on',
                            x_forwarded_for=resp['XForwardedFor'] == 'on',
                            sticky_session=resp['StickySession'] == 'on',
                            sticky_session_type=resp['StickySessionapiType'] or None,
                            cookie=resp['Cookie'] or None,
                            domain=resp['Domain'] or None,
                            uri=resp['URI'])

    def create_tcp_listener(self, load_balancer_id, listener_port,
                            backend_server_port, healthy_threshold=3,
                            unhealthy_threshold=3, listener_status=None,
                            scheduler=None, health_check=None,
                            connect_timeout=None, interval=None,
                            connect_port=None, persistence_timeout=None):
        """Create a TCP SLB Listener

        Args:
            load_balancer_id (str): LoadBalancerId unique identifier of the
                SLB.
            listener_port (int): Port for the SLB to listen on
            backend_server_port (int): Port to send traffic to on the back-end
            healthy_threshold (int): Number of successful healthchecks before
                considering the listener healthy. Default 3.
            unhealthy_threshold (int): Number of failed healthchecks before
                considering the listener unhealthy.
                Default 3.
            TCPListener arguments:

            listener_status (str): 'active' (default) or 'stopped'.
            scheduler (str): wrr or wlc. Round Robin (default) or
                Least Connections.
            health_check (bool): True for 'on' and False for 'off' (default)
            connect_timeout (int): number of seconds to timeout and fail a
                health check
            interval (int): number of seconds between health checks
            connect_port (int): defaults to backend_server_port
            persistence_timeout (int): number of seconds to hold TCP
                connection open
        """
        params = {'Action': 'CreateLoadBalancerTCPListener',
                  'LoadBalancerId': load_balancer_id,
                  'ListenerPort': int(listener_port),
                  'BackendServerPort': int(backend_server_port),
                  }

        if healthy_threshold is not None:
            params['HealthyThreshold'] = healthy_threshold
        if unhealthy_threshold is not None:
            params['UnhealthyThreshold'] = unhealthy_threshold
        if listener_status:
            params['ListenerStatus'] = listener_status
        if scheduler:
            params['Scheduler'] = scheduler
        if health_check is not None:
            params['HealthCheck'] = 'on' if health_check else 'off'
        if connect_timeout is not None:
            params['ConnectTimeout'] = connect_timeout
        if interval is not None:
            params['Interval'] = interval
        if connect_port is not None:
            params['ConnectPort'] = connect_port
        if persistence_timeout is not None:
            params['PersistenceTimeout'] = int(persistence_timeout)

        self.get(params)

    def create_http_listener(self, load_balancer_id, listener_port,
                             backend_server_port, bandwidth, sticky_session,
                             health_check, healthy_threshold=3,
                             unhealthy_threshold=3,
                             scheduler=None, connect_timeout=None,
                             interval=None, x_forwarded_for=None,
                             sticky_session_type=None,
                             cookie_timeout=None, cookie=None,
                             domain=None, uri=None):
        """Create an HTTP SLB Listener

        Args:
            load_balancer_id (str): LoadBalancerId unique identifier of the
                SLB.
            listener_port (int): Port for the SLB to listen on
            backend_server_port (int): Port to send traffic to on the back-end
            bandwidth (int): The peak burst speed of the network.
                Optional values: - 1|1 - 1000Mbps
                For the paybybandwidth intances, the peak
                burst speed of all Listeners should not exceed
                the Bandwidth value in SLB instance creation,
                and the Bandwidth value must not be set to - 1.
                For paybytraffic instances, this value can be set
                to - 1, meaning there is no restriction on
                bandwidth peak speed.
            sticky_session (str): on or off
            healthy_threshold (int): Number of successful healthchecks before
                considering the listener healthy. Default 3.
            unhealthy_threshold (int): Number of failed healthchecks before
                considering the listener unhealthy. Default 3.
            health_check (str): 'on' and 'off' (default)
        HTTPListener arguments:
            scheduler (str): wrr or wlc. Round Robin (default) or
                Least Connections.
            connect_timeout (int): number of seconds to timeout and fail a
                health check
            interval (int): number of seconds between health checks
            x_forwarded_for (bool): wether or not to append ips to
                x-fordwarded-for http header
            sticky_session_type (str):
                'insert' to have the SLB add a cookie to requests
                'server' to have the SLB look for a server-injected cookie
                sticky_session must be 'on'
            cookie_timeout (int [0-86400]):
                Lifetime of cookie in seconds. Max 1 day.
                sticky_session must be 'on'
            cookie (str):
                The Cookie key to use as sticky_session indicator.
                sticky_session_type must be 'server'
            domain (str): the Host header to use for the health check
            uri (str): URL path for healthcheck. E.g. /health
        """
        params = {'Action': 'CreateLoadBalancerHTTPListener',
                  'LoadBalancerId': load_balancer_id,
                  'ListenerPort': int(listener_port),
                  'BackendServerPort': int(backend_server_port),
                  'Bandwidth': int(bandwidth),
                  'StickySession': sticky_session,
                  'HealthCheck': health_check,
                  }
        if healthy_threshold is not None:
            params['HealthyThreshold'] = healthy_threshold
        if unhealthy_threshold is not None:
            params['UnhealthyThreshold'] = unhealthy_threshold
        if scheduler:
            params['Scheduler'] = scheduler
        if connect_timeout is not None:
            params['ConnectTimeout'] = connect_timeout
        if interval is not None:
            params['Interval'] = interval
        if x_forwarded_for is not None:
            params['XForwardedFor'] = 'on' if x_forwarded_for else 'off'
        if sticky_session_type is not None:
            params['StickySessionapiType'] = sticky_session_type
        if cookie_timeout is not None:
            params['CookieTimeout'] = cookie_timeout
        if cookie is not None:
            params['Cookie'] = cookie
        if domain is not None:
            params['Domain'] = domain
        if uri is not None:
            params['URI'] = uri

        self.get(params)

    def update_tcp_listener(self, load_balancer_id, listener_port,
                            healthy_threshold=None, unhealthy_threshold=None,
                            scheduler=None, health_check=None,
                            connect_timeout=None, interval=None,
                            connect_port=None, persistence_timeout=None):
        """Update an existing TCP SLB Listener

        Args:
            load_balancer_id (str): LoadBalancerId unique identifier of the
                SLB.
            listener_port (int): Port for the SLB to listen on
            healthy_threshold (int): Number of successful healthchecks before
                considering the listener healthy. Default 3.
            unhealthy_threshold (int): Number of failed healthchecks before
                considering the listener unhealthy.
                Default 3.
            scheduler (str): wrr or wlc. Round Robin (default) or
                Least Connections.
            health_check (bool): True for 'on' and False for 'off' (default)
            connect_timeout (int): number of seconds to timeout and fail a
                health check
            interval (int): number of seconds between health checks
            connect_port (int): defaults to backend_server_port
            persistence_timeout (int): number of seconds to hold TCP
                connection open
        """
        params = {'Action': 'SetLoadBalancerTCPListenerAttribute',
                'LoadBalancerId': load_balancer_id,
                'ListenerPort': listener_port}
        if healthy_threshold != None:
            params['HealthyThreshold'] = healthy_threshold
        if unhealthy_threshold != None:
            params['UnhealthyThreshold'] = unhealthy_threshold
        if scheduler != None:
            params['Scheduler'] = scheduler
        if health_check != None:
            params['HealthCheck'] = 'on' if health_check else 'off'
        if connect_timeout != None:
            params['ConnectTimeout'] = connect_timeout
        if interval != None:
            params['Interval'] = interval
        if connect_port != None:
            params['ConnectPort'] = connect_port
        if persistence_timeout != None:
            params['PersistenceTimeout'] = persistence_timeout

        self.get(params)

    def update_http_listener(self, load_balancer_id, listener_port,
                             healthy_threshold=None, unhealthy_threshold=None,
                             scheduler=None, health_check=None,
                             health_check_timeout=None, interval=None,
                             x_forwarded_for=None, sticky_session=None,
                             sticky_session_type=None, cookie_timeout=None,
                             cookie=None, domain=None, uri=None):
        """Update an existing HTTP SLB Listener

        Args:

            load_balancer_id (str): LoadBalancerId unique identifier of the
                SLB.
            listener_port (int): Port for the SLB to listen on
            healthy_threshold (int): Number of successful healthchecks before
                considering the listener healthy. Default 3.
            unhealthy_threshold (int): Number of failed healthchecks before
                considering the listener unhealthy. Default 3.
            scheduler (str): wrr or wlc. Round Robin (default) or
                Least Connections.
            health_check (bool): True for 'on' and False for 'off' (default)
            health_check_timeout (int): number of seconds to timeout and fail a
                health check
            interval (int): number of seconds between health checks
            x_forwarded_for (bool): wether or not to append ips to
                x-fordwarded-for http header
            sticky_session (bool): use slb sticky sessions. default false.
            sticky_session_type (str):
                'insert' to have the SLB add a cookie to requests
                'server' to have the SLB look for a server-injected cookie
                sticky_session must be 'on'
            cookie_timeout (int [0-86400]):
                Lifetime of cookie in seconds. Max 1 day.
                sticky_session must be 'on'
            cookie (str):
                The Cookie key to use as sticky_session indicator.
                sticky_session_type must be 'server'
            domain (str): the Host header to use for the health check
            uri (str): URL path for healthcheck. E.g. /health
        """

        params = {'Action': 'SetLoadBalancerHTTPListenerAttribute',
                  'LoadBalancerId': load_balancer_id,
                  'ListenerPort': int(listener_port),
                  }

        if healthy_threshold is not None:
            params['HealthyThreshold'] = healthy_threshold
        if unhealthy_threshold is not None:
            params['UnhealthyThreshold'] = unhealthy_threshold
        if scheduler:
            params['Scheduler'] = scheduler
        if health_check is not None:
            params['HealthCheck'] = 'on' if health_check else 'off'
        if health_check_timeout is not None:
            params['HealthCheckTimeout'] = health_check_timeout
        if interval is not None:
            params['Interval'] = interval
        if x_forwarded_for is not None:
            params['XForwardedFor'] = 'on' if x_forwarded_for else 'off'
        if sticky_session is not None:
            params['StickySession'] = 'on' if sticky_session else 'off'
        if sticky_session_type is not None:
            params['StickySessionapiType'] = sticky_session_type
        if cookie_timeout is not None:
            params['CookieTimeout'] = cookie_timeout
        if cookie is not None:
            params['Cookie'] = cookie
        if domain is not None:
            params['Domain'] = domain
        if uri is not None:
            params['URI'] = uri

        self.get(params)

    def start_load_balancer_listener(self, load_balancer_id, listener_port):
        """Start a listener

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId
            listener_port (int): The listener port to activate
        """
        params = {
            'Action': 'StartLoadBalancerListener',
            'LoadBalancerId': str(load_balancer_id),
            'ListenerPort': int(listener_port)
        }

        self.get(params)

    def stop_load_balancer_listener(self, load_balancer_id, listener_port):
        """Stop a listener

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId
            listener_port (int): The listener port to activate
        """
        params = {
            'Action': 'StopLoadBalancerListener',
            'LoadBalancerId': str(load_balancer_id),
            'ListenerPort': int(listener_port)
        }

        self.get(params)

    def get_backend_servers(self, load_balancer_id, listener_port=None):
        """Get backend servers for a given load balancer and its listener port.

        If listener_port is not specified, all listeners are listed separately.

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.
            listener_port (int, optional): the port to get backend server
                statuses for

        Returns:
            List of ListenerStatus
        """
        params = {
            'Action': 'DescribeBackendServers',
            'LoadBalancerId': load_balancer_id,
        }
        if listener_port is not None:
            params['ListenerPort'] = listener_port

        listeners = []
        resp = self.get(params)
        for listener in resp['Listeners']['Listener']:
            backends = []
            for bs in listener['BackendServers']['BackendServer']:
                backends.append(
                    BackendServerStatus(bs['ServerId'],
                                        bs['ServerHealthStatus']))
            listeners.append(
                ListenerStatus(listener['ListenerPort'], backends))

        return listeners

    def get_backend_server_ids(self, load_balancer_id, listener_port=None):
        backends = []
        statuses = self.get_backend_servers(load_balancer_id, listener_port)
        for status in statuses:
            backends.extend([bs.server_id for bs in status.backend_servers])

        return list(set(backends))

    def remove_backend_servers(self, load_balancer_id, backend_servers):
        """Remove backend servers from a load balancer
           Note: the SLB API ignores Weight when Removing Backend Servers. So
           you're probably better off using remove_backend_server_id anyway.

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.
            backend_servers (list of BackendServer): the backend servers to
                remove
        """
        params = {
            'Action': 'RemoveBackendServers',
            'LoadBalancerId': load_balancer_id
        }

        backends = []
        for bs in backend_servers:
                backends.append({'ServerId': bs.instance_id})

        params['BackendServers'] = backends

        return self.get(params)

    def remove_backend_server_ids(self, load_balancer_id, backend_server_ids):
        """Helper wrapper to remove backend server IDs specified from the SLB
           specified.

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.
            backend_server_ids (list of str): the backend server ids to remove
        """
        backends = [BackendServer(bsid, None) for bsid in backend_server_ids]
        return self.remove_backend_servers(load_balancer_id, backends)

    def add_backend_servers(self, load_balancer_id, backend_servers):
        """Add backend servers to a load balancer

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.
            backend_servers (list of BackendServer): the backend servers to add
        """
        params = {
            'Action': 'AddBackendServers',
            'LoadBalancerId': load_balancer_id
        }

        backends = []
        for bs in backend_servers:
            if bs.weight is not None:
                backends.append(
                    {'ServerId': bs.instance_id, 'Weight': bs.weight})
            else:
                backends.append({'ServerId': bs.instance_id})

        params['BackendServers'] = backends

        return self.get(params)

    def add_backend_server_ids(self, load_balancer_id, backend_server_ids):
        """Helper wrapper to add backend server IDs specified to the SLB
           specified.

        Args:
            load_balancer_id (str): Aliyun SLB LoadBalancerId to retrieve.
            backend_server_ids (list of str): the backend server ids to add
        """
        backends = [BackendServer(bsid, None) for bsid in backend_server_ids]
        return self.add_backend_servers(load_balancer_id, backends)

    def deregister_backend_server_ids(self, server_ids):
        """Helper wrapper to get load balancers with the server id in them and
        remove the server from each load balancer.

        Args:
            server_id (List of str): List of Aliyun ECS Instance IDs

        Returns:
            List of SLB IDs that were modified.

        """
        lbs = collections.defaultdict(list)
        for instance_id in server_ids:
            for lb_status in self.get_all_load_balancer_status(instance_id):
                lbs[lb_status.load_balancer_id].append(instance_id)
        for lb_id, bs_ids in lbs.iteritems():
            self.remove_backend_server_ids(lb_id, list(set(bs_ids)))

        return lbs.keys()

    def deregister_backend_servers(self, backend_servers):
        return (
            self.deregister_backend_server_ids(
                [bs.instance_id for bs in backend_servers])
        )
