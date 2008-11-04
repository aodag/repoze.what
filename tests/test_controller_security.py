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

"""
Tests for the authorization mechanisms.

"""

import tg, pylons
from tg.controllers import TGController
from tg.decorators import expose
from repoze.what import authorize
from nose.tools import eq_

from base import TestWSGIController, make_app, setup_session_dir, \
                 teardown_session_dir


def setup():
    setup_session_dir()


def _teardown():
    teardown_session_dir()


class SubController1(TGController):
    """Mock TG2 subcontroller"""
    
    @expose()
    def index(self):
        return 'hello sub1'
    
    @expose()
    def in_group(self):
        return 'in group'


class BasicTGController(TGController):
    """Mock TG2 controller"""

    sub1 = SubController1()
    
    @expose()
    def index(self, **kwargs):
        return 'hello world'

    @expose()
    def default(self, remainder):
        return "Main Default Page called for url /%s" % remainder
    
    @expose()
    @authorize.require(authorize.in_group('admins'))
    def admin(self):
        return 'got to admin'
    
    @expose()
    @authorize.require(authorize.in_all_groups('developers', 'admins'))
    def all_groups(self):
        return 'got to all groups'

    @expose()
    @authorize.require(authorize.in_any_group('php', 'trolls'))
    def any_groups(self):
        return 'got to any groups'

    @expose()
    @authorize.require(authorize.is_user('rms'))
    def rms_user(self):
        return 'got to promote freedomware'
    
    @expose()
    @authorize.require(authorize.has_permission('edit-site'))
    def editsite_perm_only(self):
        return 'got to edit'
    
    @expose()
    @authorize.require(authorize.has_any_permission('commit'))
    def commit_perm(self):
        return 'got to commit'

    @expose()
    @authorize.require(authorize.has_all_permissions('commit', 'edit-site'))
    def all_perm(self):
        return 'got to all perm'

    @expose()
    @authorize.require(authorize.not_anonymous())
    def not_anon(self):
        return 'got to not anon'
    
    @expose()
    def redirect_me(self, target, **kw):
        tg.redirect(target, kw)


class TestTGController(TestWSGIController):
    """Test case for the mock TG controller and its subcontroller"""
    
    def __init__(self, *args, **kargs):
        TestWSGIController.__init__(self, *args, **kargs)
        self.app = make_app(BasicTGController)
    
    def _test_index(self):
        resp = self.app.get('/index/')
        assert 'hello' in resp.body
    
    def test_group_no_auth(self):
        resp = self.app.get('/admin')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_group_with_auth(self):
        resp = self.app.get('/login_handler?login=rms&password=freedom')
        resp = self.app.get('/admin')
        eq_(resp.body, 'got to admin')

    def test_all_groups_no_auth(self):
        resp = self.app.get('/login_handler?login=rasmus&password=php')
        resp = self.app.get('/all_groups')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_all_groups(self):
        resp = self.app.get('/login_handler?login=rms&password=freedom')
        resp = self.app.get('/all_groups')
        eq_(resp.body, 'got to all groups')

    def test_any_groups_no_auth(self):
        resp = self.app.get('/login_handler?login=linus&password=freedomware')
        resp = self.app.get('/any_groups')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_any_groups(self):
        resp = self.app.get('/login_handler?login=sballmer&password=developers')
        resp = self.app.get('/any_groups')
        eq_(resp.body, 'got to any groups')

    def test_no_auth_not_anon(self):
        resp = self.app.get('/not_anon')
        assert resp.body.startswith('302 Found'), resp.body

    def test_not_anon(self):
        resp = self.app.get('/login_handler?login=linus&password=linux')
        resp = self.app.get('/not_anon')
        eq_(resp.body, 'got to not anon')

    def test_no_auth_is_user(self):
        resp = self.app.get('/login_handler?login=sballmer&password=developers')
        resp = self.app.get('/rms_user')
        assert resp.body.startswith('302 Found'), resp.body

    def test_is_user(self):
        resp = self.app.get('/login_handler?login=rms&password=freedom')
        resp = self.app.get('/rms_user')
        eq_(resp.body, 'got to promote freedomware')

    def test_no_auth_perm(self):
        resp = self.app.get('/login_handler?login=sballmer&password=developers')
        resp = self.app.get('/editsite_perm_only')
        assert resp.body.startswith('302 Found'), resp.body

    def test_perm(self):
        resp = self.app.get('/login_handler?login=rms&password=freedom')
        resp = self.app.get('/editsite_perm_only')
        eq_(resp.body, 'got to edit')

    def test_no_auth_any_perm(self):
        resp = self.app.get('/login_handler?login=linus&password=freedomware')
        resp = self.app.get('/commit_perm')
        assert resp.body.startswith('302 Found'), resp.body

    def test_any_perm(self):
        resp = self.app.get('/login_handler?login=rms&password=freedom')
        resp = self.app.get('/commit_perm')
        eq_(resp.body, 'got to commit')

    def test_no_auth_all_perm(self):
        resp = self.app.get('/login_handler?login=linus&password=freedomware')
        resp = self.app.get('/all_perm')
        assert resp.body.startswith('302 Found'), resp.body

    def test_all_perm(self):
        resp = self.app.get('/login_handler?login=linus&password=linux')
        resp = self.app.get('/all_perm')
        eq_(resp.body, 'got to all perm')
        
    def test_sub_in_admin(self):
        resp = self.app.get('/login_handler?login=sballmer&password=developers')
        resp = self.app.get('/sub1/in_group')
        eq_(resp.body, 'in group')
