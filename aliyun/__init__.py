"""
Aliyun API
==========

The Aliyun API is well-documented at `dev.aliyun.com <http://dev.aliyun.com/thread.php?spm=0.0.0.0.MqTmNj&fid=8>`_. 
Each service's API is very similar: There are regions, actions, and each action has many parameters.
It is an OAuth2 API, so you need to have an ID and a secret. You can get these from the Aliyun management console.

Authentication
==============

You will need security credentials for your Aliyun account. You can view and 
create them in the `Aliyun management console <http://console.aliyun.com>`_. This 
library will look for credentials in the following places:

 1. Environment variables `ALI_ACCESS_KEY_ID` and `ALI_SECRET_ACCESS_KEY`
 2. An ini-style configuration file at `~/.aliyun.cfg` with contents like:
   ::
    
    [default]
    access_key_id=xxxxxxxxxxxxx
    secret_access_key=xxxxxxxxxxxxxxxxxxxxxxx
   ..

 3. A system-wide version of that file at /etc/aliyun.cfg with similar contents.

We recommend using environment variables whenever possible.

Main Interfaces
===============

The main components of python-aliyun are ECS and SLB. Other Aliyun products will
be added as API support develops. Within each Aliyun product, we tried to 
implement every API Action variation available. We used a boto-style design 
where most API interaction is done with a connection object which marshalls 
Python objects and API representations.

*ECS*:

You can create a new ECS connection and interact with ECS like this::

    import aliyun.ecs.connection
    conn = aliyun.ecs.connection.EcsConnection('cn-hangzhou')
    print conn.get_all_instance_ids()

See more at :mod:`aliyun.ecs`

*SLB*:

Similarly for SLB, get the connection object like this::

    import aliyun.slb.connection
    conn = aliyun.slb.connection.SlbConnection('cn-hangzou')
    print conn.get_all_load_balancer_ids()

See more at :mod:`aliyun.slb`

ali command
===========

The ali commandline tool is mostly used for debugging the Aliyun API interactions.
It accepts arbitrary Key=Value pairs and passes them on to the API after wrapping them.

::

    ali --region cn-hangzhou ecs Action=DescribeRegions
    ali --region cn-hangzhou slb Action=DescribeLoadBalancers

"""
