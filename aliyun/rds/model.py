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

EngineVersion = { 'MySQL': [5.5, 5.6],
				'SQLServer':['2008r2'],
				'PostgreSQL': [9.4],
				'PPAS': [9.3] }

class RDSInstanceStatus(object):

    def __init__(self, instance_id, status):
        """Constructor.

        Args:
            instance_id (str): The id of the RDS instance.
            status (str): The status of the RDS instance.
        """
        self.instance_id = instance_id
        self.status = status

    def __repr__(self):
        return u'<InstanceId %s is %s at %s>' % (
            self.instance_id, self.status, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

class RDSInstance(object):

    """An Aliyun RDS instance."""

    def __init__(
            self, instance_id, region_id, instance_type,
            description, status, security_ip_list,
            creation_time, expired_time, instance_charge_type,
            connection_string, dbinstance_net_type, max_connections, engine,
            availability_value, account_max_quantity, db_max_quantity, db_instance_memory,
            max_iops, dbinstance_type, engineversion, 
            dbinstance_storage, port):
        """"Constructor.

        Args:
            instance_id (str): The id of the RDS instance.
            region_id (str): The id of the region in which the RDS instance lies.
            instance_type (str): The spec of the instance.
            description (str): The hostname of the instance.
            status (str): The status of the instance.
            security_ip_list (list): The security group ids for the instance.
            creation_time (datetime): Its creation time.
            expired_time (datetime): The expired time for PrePaid instances.
            instance_charge_type: The charge type of instance, either PrePaid or PostPaid.
            connection_string (str): The connection address.
            dbinstance_net_type (str): The network type of the RDS instance, Internet or Intranet.
            max_connections (int): The maximum concurrent connetions of the RDS instance.
            engine (str): The database type.
            availability_value (str): The availability status of the RDS instance.
            account_max_quantity (int): The maximum account number that can be created.
            db_max_quantity (int): The maximum database number that can be created on the RDS instance.
            db_instance_memory (int): The memory of the RDS instance.
            max_iops (int): The maximum IO number per second.
            dbinstance_type (str): The type of the RDS instance, Primary/ReadOnly/Guard/Temp.
            engineversion (str): The version of the database.
            dbinstance_storage (int): The storage space of the RDS instance, in GB.
            port (int): The LISTENING port of the Database.
        """
        self.instance_id = instance_id
        self.region_id = region_id
        self.instance_type = instance_type
        self.description = description
        self.status = status
        self.security_ip_list = security_ip_list
        self.creation_time = creation_time
        self.expired_time = expired_time
        self.instance_charge_type = instance_charge_type
        self.connection_string = connection_string
        self.dbinstance_net_type = dbinstance_net_type
        self.max_connections = max_connections
        self.engine = engine
        self.availability_value = availability_value
        self.account_max_quantity = account_max_quantity
        self.db_max_quantity = db_max_quantity
        self.db_instance_memory = db_instance_memory
        self.max_iops = max_iops
        self.dbinstance_type = dbinstance_type
        self.engineversion = engineversion
        self.dbinstance_storage = dbinstance_storage
        self.port = port

    def __repr__(self):
        return '<Instance %s at %s>' % (self.instance_id, id(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)
