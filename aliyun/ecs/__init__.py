"""
Aliyun ECS
==========

To interact with the ECS API, use :class:`aliyun.ecs.connection.EcsConnection`.
::
    import aliyun.ecs.connection
    conn = aliyun.ecs.connection.EcsConnection('cn-hangzhou')
    my_instance_ids = conn.get_all_instance_ids()
    for instance_id in my_instance_ids:
        print "Instance ID: ", instance_id
        instance = conn.get_instance(instance_id)
        print "Instance object: ", instance
..

The many methods in :class:`aliyun.ecs.connection.EcsConnection` are split into two categories:
    1. Direct API implementation
    2. Helper and wrapper functionality

The following ECS API actions are nearly fully supported:
    * DescribeRegions
    * DescribeInstanceStatus
    * DescribeInstanceAttribute
    * StartInstance
    * StopInstance
    * RebootInstance
    * DeleteInstance
    * ModifyInstanceAttribute
    * CreateInstance
    * AllocatePublicIpAddress
    * DescribeInstanceTypes
    * JoinSecurityGroup
    * LeaveSecurityGroup
    * DescribeSecurityGroups
    * CreateSecurityGroup
    * DescribeSecurityGroupAttribute
    * DeleteSecurityGroup
    * AuthorizeSecurityGroup
    * RevokeSecurityGroup
    * DescribeInstanceDisks
    * DeleteSnapshot
    * DescribeSnapshotAttribute
    * DescribeSnapshots
    * CreateSnapshot
    * DescribeImages
    * DeleteImage
    * CreateImage

Additional helper functionality is provided by:
    * :func:`aliyun.ecs.connection.EcsConnection.get_all_region_ids`
    * :func:`aliyun.ecs.connection.EcsConnection.get_all_instance_ids`
    * :func:`aliyun.ecs.connection.EcsConnection.create_and_start_instance`
    * :func:`aliyun.ecs.connection.EcsConnection.get_security_group_ids`
    * :func:`aliyun.ecs.connection.EcsConnection.add_group_rule`
    * :func:`aliyun.ecs.connection.EcsConnection.add_internal_cidr_ip_rule`
    * :func:`aliyun.ecs.connection.EcsConnection.add_external_cidr_ip_rule`
    * :func:`aliyun.ecs.connection.EcsConnection.remove_group_rule`
    * :func:`aliyun.ecs.connection.EcsConnection.remove_internal_cidr_ip_rule`
    * :func:`aliyun.ecs.connection.EcsConnection.remove_external_cidr_ip_rule`

The API's models are reflected in :mod:`aliyun.ecs.model` and are generally not intended for direct use.
"""
