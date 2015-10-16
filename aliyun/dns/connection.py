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

import json
import time
import datetime
import logging

import dateutil.parser

from aliyun.connection import Connection

BLOCK_TILL_RUNNING_SECS = 600

logger = logging.getLogger(__name__)

class Error(Exception):

    """Base exception class for this module."""


class DnsConnection(Connection):
    """A connection to Aliyun DNS service.

    Args:
        region_id (str): NOT IN USE FOR DNS
                         But needed for backward comptibility
                         The id of the region to connect to.
        access_key_id (str): The access key id.
        secret_access_key (str): The secret access key.
    """
    def __init__(self, region_id, access_key_id=None, secret_access_key=None):
        super(DnsConnection, self).__init__(
	    region_id, 'dns', access_key_id=access_key_id,
	    secret_access_key=secret_access_key)
    
    def add_record(self, rr=None, type='A', value=None, domainname="quixey.be"):
        """
	Add a DNS record to specified Domain.

	Args:
	    rr (str): Resource Record to add.
	    value (str): The IP address of the RR.
	    type (str): Type of the Resource Record, A, PTR, CNAME for instance.
	    domainname (str): The domain name the rr will be added into.
	
	Returns: 
	"""

	if rr is None or value is None:
	    exit("ERROR: Both RR and its value MUST be supplied.")

	params = {'Action': 'AddDomainRecord', \
		  'Type': type, \
		  'DomainName': domainname, \
		  'RR': rr, \
		  'value': value, \
		 }
        return self.get(params)

    def get_all_records(self, domainname="quixey.be"):
        """
	Get all records of the Domain.

	Args:
	    domainname (str): The domain name that all records belong.

	Returns: All records in the Domain.
	"""

	params = {'Action': 'DescribeDomainRecords', \
	          'DomainName': domainname, \
		 }

        return self.get(params)['DomainRecords']['Record']

    def get_record_id(self, rr, value, domainname):
        """
	Get the RecordId of the specified RR & Value pair.

	Args:
	    rr (str): Resource Record to query, such as www
	    value (str): The IP address of the RR.
	    domainname (str): The domain name the rr will be added into.

	Returns: The RecordId
	"""

	if rr is None or value is None:
	    exit("ERROR: Please specify the RR and its IP addr.")

	all_records = self.get_all_records(domainname)
	for record in all_records:
	    if record['RR'] == rr and record['Value'] == value:
	        return record['RecordId']

        return

    def delete_record(self, rr=None, value=None, domainname="quixey.be"):
        """
	Delete the specified record.
        
	Args:
	    rr (str): Resource Record to query, such as www
	    value (str): The IP address of the RR.
	    domainname (str): The domain name the rr will be added into.

	"""

	if rr is None or value is None:
	    exit("ERROR: Please specify the RR and its IP addr.")

	record_id = self.get_record_id(rr, value, domainname)
        if record_id:
	    params = {'Action': 'DeleteDomainRecord', \
	              'RecordId': record_id, \
		     }
            return self.get(params)
	else:
	    logger.debug('No such record.')
