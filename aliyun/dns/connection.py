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
    def __init__(self, region_id='cn-hangzhou', access_key_id=None, secret_access_key=None):
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
	    abort("ERROR: Both RR and its value MUST be supplied.")

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
	all_records = []
	params = {'Action': 'DescribeDomainRecords', \
	          'DomainName': domainname, \
		 }

	for resp in self.get(params, paginated=True):
		for item in resp['DomainRecords']['Record']:
			all_records.append(item)
	return all_records

    def get_record_id(self, rr, value, type='A', domainname='quixey.be'):
        """
	Get the RecordId of the specified RR & Value pair.

	Args:
	    rr (str): Resource Record to query, such as www
	    value (str): The IP address of the RR
	    type (str): The Resource Record Type, such as A, CNAME, MX
	    domainname (str): The domain name the rr will be added into

	Returns: The RecordId
	"""

	if rr is None or value is None:
	    abort("ERROR: Please specify the RR and its IP address.")

	params = {'Action': 'DescribeDomainRecords', \
		  'DomainName': domainname, \
		  'RRKeyWord': rr, \
		  'TypeKeyWord': type, \
		  'ValueKeyWord': value, \
		 } 
        return self.get(params)['DomainRecords']['Record'][0]['RecordId']

    def delete_record(self, rr=None, value=None, type='A', domainname="quixey.be"):
        """
	Delete the specified record.
        
	Args:
	    rr (str): Resource Record to query, such as www
	    value (str): The IP address of the RR.
	    domainname (str): The domain name the rr will be added into.
	"""

	if rr is None or value is None:
	    abort("ERROR: Please specify the RR and its IP address.")

	record_id = self.get_record_id(rr, value, type, domainname)
        if record_id:
	    params = {'Action': 'DeleteDomainRecord', \
	              'RecordId': record_id, \
		     }
            return self.get(params)
	else:
	    logger.debug('No such record.')
