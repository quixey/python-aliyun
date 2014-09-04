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

import base64
import hmac
import hashlib
import json
import logging
import os
import time
import urllib
import urllib2
import urlparse
import uuid
import sys

from collections import namedtuple
from ConfigParser import ConfigParser
from hashlib import sha1


PAGE_SIZE = 50


class Error(Exception):

    """Base exception class for this module."""


def find_credentials():
    """Tries to get the aliyun credentials from the following in priority:

     * environment variables
     * config file

    The environment variables to use are:

     * ALI_ACCESS_KEY_ID
     * ALI_SECRET_ACCESS_KEY

    If both of these are not found, it then looks for config files at::

        $HOME/.aliyun.cfg
        /etc/aliyun.cfg

    The format of the file must be::

        [default]
        access_key_id=ACCESS_KEY
        secret_access_key=SECRET_KEY
    """
    creds = namedtuple('Credentials', 'access_key_id secret_access_key')

    creds.access_key_id = os.getenv('ALI_ACCESS_KEY_ID', None)
    creds.secret_access_key = os.getenv('ALI_SECRET_ACCESS_KEY', None)
    if creds.access_key_id != None and creds.secret_access_key != None:
        return creds

    cfg_path = os.path.join(os.getenv('HOME', '/root/'), '.aliyun.cfg')
    cp = ConfigParser()

    if os.path.exists(cfg_path):
        cp.read(cfg_path)
    else:
        cp.read('/etc/aliyun.cfg')

    if cp.has_section('default') and cp.has_option('default', 'access_key_id'):
        creds.access_key_id = cp.get('default', 'access_key_id')
        creds.secret_access_key = cp.get('default', 'secret_access_key')
        return creds
    else:
        raise Error("Could not find credentials.")


class Connection(object):

    def __init__(self, region_id, service, access_key_id=None,
                 secret_access_key=None):
        """Constructor.

        If the access and secret key are not provided the credentials are
        looked for in $HOME/.aliyun.cfg or /etc/aliyun.cfg.

        Args:
            region_id (str): The id of the region to connect to.
            service (str): The service to connect to. Current supported are:
                ecs, slb.
            access_key_id (str): The access key id.
            secret_access_key (str): The secret access key.
        """
        if not region_id:
            raise Error('region_id is required')
        if not service:
            raise Error('service is required')

        self.region_id = region_id
        if service == 'ecs':
            self.service = 'https://ecs.aliyuncs.com'
            self.version = '2014-05-26'
        elif service == 'slb':
            self.service = 'https://slb.aliyuncs.com'
            self.version = '2013-02-21'
        else:
            raise NotImplementedError(
                'Currently only "ecs" and "slb" are supported.')

        if access_key_id is None or secret_access_key is None:
            creds = find_credentials()
            self.access_key_id = creds.access_key_id
            self.secret_access_key = creds.secret_access_key
        else:
            self.access_key_id = access_key_id
            self.secret_access_key = secret_access_key

        self.logging= logging.getLogger()
        self.logging.debug("%s connection to %s created" % (service, region_id))

    def _percent_encode(self, request):
        encoding = sys.stdin.encoding
        if encoding == None:
            encoding = sys.getdefaultencoding()

        res = urllib.quote(
            request.decode(encoding).encode('utf8'),
            '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def _compute_signature(self, parameters):
        sortedParameters = sorted(
            parameters.items(),
            key=lambda parameters: parameters[0])

        canonicalizedQueryString = ''
        for (k, v) in sortedParameters:
            canonicalizedQueryString += '&' + \
                self._percent_encode(k) + '=' + \
                self._percent_encode(unicode(v))

        stringToSign = 'GET&%2F&' + \
            self._percent_encode(canonicalizedQueryString[1:])

        h = hmac.new(self.secret_access_key + "&", stringToSign, sha1)
        signature = base64.encodestring(h.digest()).strip()
        return signature

    def _build_request(self, params):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Use defaults...
        parameters = {
            'Format': 'JSON',
            'Version': self.version,
            'AccessKeyId': self.access_key_id,
            'SignatureVersion': '1.0',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid1()),
            'TimeStamp': timestamp,
            'RegionId': self.region_id
        }
        # And overwrite some...
        parameters.update(params)

        signature = self._compute_signature(parameters)
        parameters['Signature'] = signature

        url = "%s/?%s" % (self.service, urllib.urlencode(parameters))
        request = urllib2.Request(url)
        return request

    def _get(self, request):
        self.logging.debug('URL requested: %s' % request.get_full_url())
        try:
            conn = urllib2.urlopen(request)
            response = conn.read()
            encoding = conn.headers['content-type'].split('charset=')[-1]
            unicode_response = unicode(response, encoding)
            self.logging.debug('URL response: %s' % unicode_response)
            return json.loads(unicode_response)
        except urllib2.HTTPError as e:
            self.logging.error('Error GETing URL: %s' % request.get_full_url())
            raise Error(e.read())

    def _get_remaining_pages(self, total_count):
        """Get the remaining pages for the given count.

        Args:
            total_count: The total count of items.
        """
        if total_count <= PAGE_SIZE:
            return 0

        pages = (total_count - PAGE_SIZE) / PAGE_SIZE
        return (
            pages + 1 if ((total_count - PAGE_SIZE) % PAGE_SIZE) > 0 else pages
        )

    def _perform_paginated_queries(self, params):
        """Perform paginated queries with the given params.

        Args:
            params: The params for the queries, without the PageSize and
                PageNumber.

        Return:
            The list of responses - one response for each page.
        """
        responses = []
        params['PageSize'] = str(PAGE_SIZE)
        resp = self.get(params)
        total_count = resp['TotalCount']
        if total_count == 0:
            return [resp]

        responses.append(resp)

        remaining_pages = self._get_remaining_pages(total_count)
        i = 1
        while i <= remaining_pages:
            params['PageNumber'] = str(i + 1)
            responses.append(self.get(params))
            i += 1

        return responses

    def get(self, params, paginated=False):
        if paginated:
            return self._perform_paginated_queries(params)

        request = self._build_request(params)
        return self._get(request)
