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

import os
import mox
import unittest

from collections import namedtuple

import aliyun.connection

class CredentialsTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def testEnvVars(self):
        self.mox.StubOutWithMock(os, 'getenv')
        os.getenv('ALI_ACCESS_KEY_ID', None).AndReturn('key')
        os.getenv('ALI_SECRET_ACCESS_KEY', None).AndReturn('secret')
        self.mox.ReplayAll()

        creds = namedtuple('Credentials', 'access_key_id secret_access_key')
        creds.access_key_id = 'key'
        creds.secret_access_key = 'secret'

        given_creds = aliyun.connection.find_credentials()

        self.assertEqual(creds.access_key_id, given_creds.access_key_id)
        self.assertEqual(creds.secret_access_key, given_creds.secret_access_key)

        self.mox.VerifyAll()

    #def testLocalConfig(self):
    #    self.mox.StubOutWithMock(os, 'getenv')
    #    os.getenv('ALI_ACCESS_KEY_ID', None).AndReturn(None)
    #    os.getenv('ALI_SECRET_ACCESS_KEY', None).AndReturn(None)
    #    os.getenv('HOME', '/root/').AndReturn('/home/test/')
    #    self.mox.StubOutWithMock(os.path, 'exists')
    #    os.path.exists('/home/test/.aliyun.cfg').AndReturn(True)
    #    cp = ConfigParser.ConfigParser()
    #    self.mox.CreateMock(ConfigParser.ConfigParser)
    #    self.cp = ConfigParser.ConfigParser()
    #    self.mox.StubOutWithMock(ConfigParser.ConfigParser, 'read')
    #    self.mox.StubOutWithMock(ConfigParser.ConfigParser, 'has_section')
    #    self.mox.StubOutWithMock(ConfigParser.ConfigParser, 'has_option')
    #    self.mox.StubOutWithMock(ConfigParser.ConfigParser, 'get')
    #    self.cp.read('/home/test/.aliyun.cfg')
    #    self.cp.has_section('default').AndReturn(True)
    #    self.cp.has_option('default', 'access_key_id').AndReturn(True)
    #    self.cp.get('default', 'access_key_id').AndReturn('key')
    #    self.cp.get('default', 'secret_access_key').AndReturn('secret')
    #    self.mox.ReplayAll()

    #    given_creds = aliyun.connection.find_credentials()
    #    self.assertEqual(given_creds.access_key_id, 'key')
    #    self.assertEqual(given_creds.secret_access_key, 'secret')

    #    self.mox.VerifyAll()

    def testPercentEncode(self):
        c = aliyun.connection.Connection('some_region_id',
                                         'ecs',
                                         'some_access_key_id',
                                         'some_secret_access_key')
        encoded = c._percent_encode(u'*+ ~')
        self.assertEqual(str, type(encoded))
        self.assertEqual('%2A%2B%20~', encoded)

        encoded = c._percent_encode('\xc3\xa4', encoding='utf8')
        self.assertEqual(str, type(encoded))
        self.assertEqual('%C3%A4', encoded)

        encoded = c._percent_encode('~%7E')
        self.assertEqual(str, type(encoded))
        self.assertEqual('~%257E', encoded)

        encoded = c._percent_encode(42)
        self.assertEqual(str, type(encoded))
        self.assertEqual('42', encoded)

    def testSignature(self):
        c = aliyun.connection.Connection('some_region_id',
                                         'ecs',
                                         'some_access_key_id',
                                         'some_secret_access_key')
        sig = c._compute_signature({'abc': 'def',
                                    '\xc3\xa4': 'str type',
                                    '*+ ~': '*+ ~'},
                                   encoding='utf8')
        self.assertEqual('Esu7vZK6JBsujsaQXT1AHKR5Ols=', sig)
