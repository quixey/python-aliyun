"""
Aliyun ESS
==========

To interact with the ESS API, use :class:`aliyun.ess.connection.EssConnection`.
::
    import aliyun.ess.connection
    conn = aliyun.ess.connection.EssConnection('cn-hangzhou')
..

The many methods in :class:`aliyun.ess.connection.EssConnection` are split into two categories:
    1. Direct API implementation
    2. Helper and wrapper functionality

The following ESS API actions are fully supported:
    * DescribeRegions

Additional helper functionality is provided by:
    * :func:`aliyun.ecs.connection.EcsConnection.get_all_region_ids`

The API's models are reflected in :mod:`aliyun.ess.model` and are generally not intended for direct use.
"""
