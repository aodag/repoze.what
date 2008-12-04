# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Test suite for the adapters' test utilities."""

import unittest

from repoze.what.adapters.testutil import GroupsAdapterTester, \
                                          PermissionsAdapterTester

from repoze.what.testutil import FakeGroupSourceAdapter, FakePermissionSourceAdapter

class TestGroupsAdapterTester(GroupsAdapterTester, unittest.TestCase):
    def setUp(self):
        super(TestGroupsAdapterTester, self).setUp()
        self.adapter = FakeGroupSourceAdapter()

class TestPermissionsAdapterTester(PermissionsAdapterTester, unittest.TestCase):
    def setUp(self):
        super(TestPermissionsAdapterTester, self).setUp()
        self.adapter = FakePermissionSourceAdapter()