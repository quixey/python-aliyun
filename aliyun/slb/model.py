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

import connection as slb


class Region(object):

    def __init__(self, region_id):
        self.region_id = region_id

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return u'<SLBRegion %s at %s>' % (self.region_id, id(self))


class LoadBalancerStatus(object):

    """Simple status of SLB

    Args:
        load_balancer_id (str): LoadBalancerId unique identifier of the SLB.
        load_balancer_name (str): name of the SLB.
        status (str): SLB status.
    """

    def __init__(self, load_balancer_id, load_balancer_name, status):
        self.load_balancer_id = load_balancer_id
        self.status = status

    def __repr__(self):
        return (
            '<LoadBalancerStatus %s is %s at %s>' % (
                self.load_balancer_id,
                self.status,
                id(self))
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class LoadBalancer(object):

    """An Aliyun Server Load Balancer (SLB) instance. Modeled after the
    DescribeLoadBalancerAttribute SLB API.

    Args:
        load_balancer_id (str): unique identifier of the SLB.
        region_id (str): region id for the SLB.
        load_balancer_name (str): description of the SLB.
        load_balancer_status (str): status of the SLB. 'inactive' or 'active'
        address (str): IP address of the SLB.
        address_type (str): internet vs intranet
        listener_ports (list int): Ports which have listeners
        backend_servers (list of BackendServer, optional): BackendServers to
                        put into the load balancer
    """

    def __init__(self, load_balancer_id,
                 region_id,
                 load_balancer_name,
                 load_balancer_status,
                 address,
                 address_type,
                 listener_ports,
                 backend_servers=[]):

        if load_balancer_id is None:
            raise slb.Error(
                'LoadBalancer requires load_balancer_id to be not None')

        self.load_balancer_id = load_balancer_id
        self.region_id = region_id
        self.load_balancer_name = load_balancer_name
        self.load_balancer_status = load_balancer_status
        self.address = address
        self.address_type = address_type
        self.listener_ports = listener_ports
        self.backend_servers = backend_servers

    def __repr__(self):
        return (
            '<LoadBalancer %s (%s) at %s>' % (
                self.load_balancer_id,
                self.load_balancer_name,
                id(self))
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class ListenerStatus(object):

    """Status for listener port and backend server list pairings.

    Args:
        listener_port (int): Number between 1 and 65535.
        backend_servers (list of BackendServerStatus)
    """

    def __init__(self, listener_port, backend_servers=[]):
        self.listener_port = listener_port
        self.backend_servers = backend_servers

    def __repr__(self):
        return u'<ListenerStatus %s at %s>' % (self.listener_port, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class Listener(object):

    """(Abstract by use) base class for LoadBalancerListeners

    Args:
        load_balancer_id (int, required): ID of the SLB instance
        listener_port (int, required): port the Load Balancer listens on
        backend_server_port (int, required): port number to connect to servers
        listener_status (str): 'active' (default) or 'stopped'.
        scheduler (str): wrr or wlc. Round Robin (default) or
            Least Connections.
        health_check (bool): True for 'on' and False for 'off' (default)
        healthy_threshold (int): number of health check successes to become
            healthy
        unhealthy_threshold (int): number of health check failures to become
            unhealthy
        connect_timeout (int): number of seconds to timeout and fail a health
            check
        interval (int): number of seconds between health checks
    """

    def __init__(self, load_balancer_id, listener_port, backend_server_port,
                 listener_status=None,
                 scheduler='wrr',
                 health_check=False,
                 connect_timeout=5,
                 interval=2):

        self.load_balancer_id = load_balancer_id
        self.listener_port = listener_port
        self.backend_server_port = backend_server_port
        self.listener_status = listener_status
        self.scheduler = scheduler
        self.health_check = health_check
        self.connect_timeout = connect_timeout

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class TCPListener(Listener):

    """TCP Load Balancer Listener

    Args:
        load_balancer_id (str): LoadBalancerId unique identifier of the SLB.
        listener_port (int, required): port the Load Balancer listens on
        backend_server_port (int, required): port number to connect to servers
        listener_status (str): 'active' (default) or 'stopped'.
        scheduler (str): wrr or wlc. Round Robin (default) or
            Least Connections.
        health_check (bool): True for 'on' and False for 'off' (default)
        connect_timeout (int): number of seconds to timeout and fail a health
            check
        interval (int): number of seconds between health checks
        connect_port (int): defaults to backend_server_port
        persistence_timeout (int): number of seconds to hold TCP connection
            open
    """

    def __init__(self, load_balancer_id, listener_port, backend_server_port,
                 listener_status='active',
                 scheduler='wrr',
                 health_check=False,
                 connect_timeout=5,
                 interval=2,
                 connect_port=None,
                 persistence_timeout=0):

        self.load_balancer_id = load_balancer_id
        self.listener_port = listener_port
        self.backend_server_port = backend_server_port
        self.listener_status = listener_status
        self.scheduler = scheduler
        self.health_check = health_check
        self.connect_timeout = connect_timeout

        if connect_port is None:
            connect_port = backend_server_port

        self.connect_port = connect_port
        self.persistence_timeout = persistence_timeout

        super(TCPListener, self).__init__(
            load_balancer_id, listener_port, backend_server_port,
            listener_status, scheduler, health_check, connect_timeout,
            interval)

    def __repr__(self):
        return u'<TCPListener on %s for %s at %s>' % (
            self.listener_port, self.load_balancer_id, id(self))


class HTTPListener(Listener):

    """HTTP Load Balancer Listener

    Args:
        load_balancer_id (str): LoadBalancerId unique identifier of the SLB.
        listener_port (int, required): port the Load Balancer listens on
        backend_server_port (int, required): port number to connect to servers
        listener_status (str): 'active' (default) or 'stopped'
        scheduler (str): wrr or wlc. Round Robin (default) or
            Least Connections.
        health_check (bool): True for 'on' and False for 'off' (default)
        connect_timeout (int): number of seconds to timeout and fail a health
            check
        interval (int): number of seconds between health checks
        x_forwarded_for (bool): Wether or not to append IPs to
            X-Fordwarded-For HTTP header
        sticky_session (bool): Use SLB Sticky Sessions. Default False.
        sticky_session_type (str):
            'insert' to have the SLB add a cookie to requests
            'server' to have the SLB look for a server-injected cookie
            sticky_session must be 'on'
        cookie_timeout (int [0-86400]):
            Lifetime of cookie in seconds. Max 1 day.
            sticky_session must be True.
        cookie (str):
            The Cookie key to use as sticky_session indicator.
            sticky_session_type must be 'server'
        domain (str): the Host header to use for the health check
        uri (str): URL path for healthcheck. E.g. /health
    """

    def __init__(self, load_balancer_id, listener_port, backend_server_port,
                 listener_status='active',
                 scheduler='wrr',
                 health_check=False,
                 connect_timeout=5,
                 interval=2,
                 x_forwarded_for=False,
                 sticky_session=False,
                 sticky_session_type=None,
                 cookie_timeout=None,
                 cookie=None,
                 domain=None,
                 uri=''):

        self.load_balancer_id = load_balancer_id
        self.listener_port = listener_port
        self.backend_server_port = backend_server_port
        self.listener_status = listener_status
        self.scheduler = scheduler
        self.health_check = health_check
        self.connect_timeout = connect_timeout

        super(HTTPListener, self).__init__(
            load_balancer_id, listener_port, backend_server_port,
            listener_status, scheduler, health_check, connect_timeout,
            interval)

        if sticky_session == True and sticky_session_type is None:
            raise slb.Error(
                'sticky_session_type must be specified when using '
                'sticky_session=True')
        if sticky_session_type == 'server' and cookie is None:
            raise slb.Error(
                'cookie must be specified when using '
                'sticky_session_type=server')

        self.x_forwarded_for = x_forwarded_for
        self.sticky_session = sticky_session
        self.sticky_session_type = sticky_session_type
        self.cookie_timeout = cookie_timeout
        self.cookie = cookie
        self.domain = domain
        self.uri = uri

    def __repr__(self):
        return u'<HTTPListener on %s at %s>' % (self.listener_port, id(self))


class BackendServerStatus(object):

    def __init__(self, server_id, status):
        self.server_id = server_id
        self.status = status

    def __repr__(self):
        return (
            u'<BackendServerStatus %s is %s at %s>' % (
                self.server_id,
                self.status,
                id(self))
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)


class BackendServer(object):

    """BackendServer describing ECS instances attached to an SLB

    Args:
        instance_id (str): ECS InstanceId (also SLB ServerId) attached
        weight (int): SLB weight. Between 1 and 1000. Default 100.

    Properties:
        status (str): (read-only) SLB ServerHealthStatus either 'normal' or
        'abnormal' """

    def __init__(self, instance_id, weight):
        self.instance_id = instance_id
        self.weight = weight

    def __repr__(self):
        return u'<BackendServer %s at %s>' % (self.instance_id, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

