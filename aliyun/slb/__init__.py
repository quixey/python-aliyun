"""
Aliyun SLB
==========

To interact with the SLB API, use :class:`aliyun.slb.connection.SlbConnection`.
::
    import aliyun.slb.connection
    conn = aliyun.slb.connection.SlbConnection('cn-hangzhou')
    conn.deregister_backend_server_ids(['bad_id'])
..

Generally, the API Action parameters are implemented in methods named very similar to their associated Action. Some additional helper functionality wraps some calls. The helper methods are:
    * :func:`aliyun.slb.connection.SlbConnection.get_all_region_ids`
    * :func:`aliyun.slb.connection.SlbConnection.get_all_load_balancer_ids`
    * :func:`aliyun.slb.connection.SlbConnection.get_backend_server_ids`
    * :func:`aliyun.slb.connection.SlbConnection.remove_backend_server_ids`
    * :func:`aliyun.slb.connection.SlbConnection.add_backend_server_ids`
    * :func:`aliyun.slb.connection.SlbConnection.deregister_backend_server_ids`
    * :func:`aliyun.slb.connection.SlbConnection.deregister_backend_servers`
"""
