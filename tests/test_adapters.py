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

"""Tests for the base source adapters."""

import unittest

from zope.interface import implements

from repoze.what.adapters import *

from base import FakeGroupSourceAdapter


class TestBaseSourceAdapter(unittest.TestCase):
    """
    Tests for the base source adapter.
    
    The most important thing to be checked is that it deals with its internal
    cache correctly.
    
    """
    
    def setUp(self):
        self.adapter = FakeGroupSourceAdapter()
        
    def test_cache_is_empty_initially(self):
        """No section has been loaded; the cache is clear"""
        self.assertEqual(self.adapter.loaded_sections, {})
        self.assertEqual(self.adapter.all_sections_loaded, False)
        
    def test_items_are_returned_as_sets(self):
        """The items of a section must always be returned as a Python set"""
        # Bulk fetch:
        for section in self.adapter.get_all_sections():
            assert isinstance(self.adapter.get_section_items(section), set)
    
    def test_retrieving_all_sections(self):
        self.assertEqual(self.adapter.get_all_sections(),
                         self.adapter.fake_sections)
        # Sections are in the cache now
        self.assertEqual(self.adapter.loaded_sections,
                         self.adapter.fake_sections)
        self.assertEqual(self.adapter.all_sections_loaded, True)
    
    def test_getting_section_items(self):
        self.assertEqual(self.adapter.get_section_items(u'trolls'), 
                         self.adapter.fake_sections[u'trolls'])
    
    def test_getting_items_of_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, 
                          self.adapter.get_section_items,
                          'non-existing')
    
    def test_setting_section_items(self):
        items = (u'guido', u'rasmus')
        self.adapter.set_section_items(u'trolls', items)
        self.assertEqual(self.adapter.fake_sections[u'trolls'], set(items))
    
    def test_cache_is_updated_after_setting_section_items(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Adding items...
        items = (u'linus', u'rms')
        self.adapter.set_section_items(u'developers', items)
        # Checking the cache:
        self.assertEqual(self.adapter.get_section_items(u'developers'),
                         set(items))
    
    def test_getting_sections_by_criteria(self):
        identity = {'repoze.who.userid': u'sballmer'}
        sections = set([u'trolls'])
        self.assertEqual(self.adapter.find_sections(identity), sections)
    
    def test_adding_one_item_to_section(self):
        self.adapter.include_item(u'developers', u'rasmus')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'linus', u'rasmus', u'rms')))
    
    def test_adding_many_items_to_section(self):
        self.adapter.include_items(u'developers', (u'sballmer', u'guido'))
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'rms', u'sballmer', u'linus', u'guido')))
    
    def test_cache_is_updated_after_adding_item(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Now let's add the item:
        self.adapter.include_item(u'developers', u'guido')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'linus', u'guido', u'rms')))
        # Now checking that the cache was updated:
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         self.adapter.get_section_items(u'developers'))
    
    def test_removing_one_item_from_section(self):
        self.adapter.exclude_item(u'developers', u'linus')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set([u'rms']))
    
    def test_removing_many_items_from_section(self):
        self.adapter.exclude_items(u'developers', (u'linus', u'rms'))
        self.assertEqual(self.adapter.fake_sections[u'developers'], set())
    
    def test_cache_is_updated_after_removing_item(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Now let's remove the item:
        self.adapter.exclude_item(u'developers', u'rms')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set([u'linus']))
        # Now checking that the cache was updated:
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         self.adapter.get_section_items(u'developers'))

    def test_creating_section(self):
        self.adapter.create_section('sysadmins')
        self.assertTrue(self.adapter.fake_sections.has_key('sysadmins'))
        self.assertEqual(self.adapter.fake_sections['sysadmins'],
                         set())
    
    def test_creating_existing_section(self):
        self.assertRaises(ExistingSectionError, self.adapter.create_section,
                          'developers')
    
    def test_cache_is_updated_after_creating_section(self):
        self.adapter.create_section('sysadmins')
        self.assertEqual(self.adapter.get_section_items('sysadmins'), set())
    
    def test_editing_section(self):
        items = self.adapter.fake_sections['developers']
        self.adapter.edit_section(u'developers', u'designers')
        self.assertEqual(self.adapter.fake_sections[u'designers'], items)
    
    def test_editing_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, self.adapter.edit_section,
                          u'this_section_doesnt_exit', u'new_name')
    
    def test_cache_is_updated_after_editing_section(self):
        # Loading for the first time:
        self.adapter.get_section_items('developers')
        # Editing:
        description = u'Those who write in weird languages'
        items = self.adapter.fake_sections[u'developers']
        self.adapter.edit_section(u'developers', u'coders')
        # Checking cache:
        self.assertEqual(self.adapter.get_section_items(u'coders'), items)
    
    def test_deleting_section(self):
        self.adapter.delete_section(u'developers')
        self.assertRaises(NonExistingSectionError,
                          self.adapter.get_section_items, u'designers')
    
    def test_deleting_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, self.adapter.delete_section,
                          u'this_section_doesnt_exit')
    
    def test_cache_is_updated_after_deleting_section(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Deleting:
        self.adapter.delete_section(u'developers')
        # Checking cache:
        self.assertRaises(NonExistingSectionError,
                          self.adapter.get_section_items,
                          u'developers')
    
    def test_checking_section_existence(self):
        # Existing section:
        self.adapter._check_section_existence(u'developers')
        # Non-existing section:
        self.assertRaises(NonExistingSectionError,
                          self.adapter._check_section_existence, u'designers')
    
    def test_checking_section_not_existence(self):
        # Non-existing section:
        self.adapter._check_section_not_existence(u'designers')
        # Existing section:
        self.assertRaises(ExistingSectionError,
                          self.adapter._check_section_not_existence, u'admins')
    
    def test_checking_item_inclusion(self):
        self.adapter._confirm_item_is_present(u'developers', u'linus')
        self.assertRaises(ItemNotPresentError,
                          self.adapter._confirm_item_is_present, u'developers', 
                          u'maribel')
    
    def test_checking_item_inclusion_in_non_existing_section(self):
        self.assertRaises(NonExistingSectionError,
                          self.adapter._confirm_item_is_present, u'users', 
                          u'linus')
    
    def test_checking_item_exclusion(self):
        self.adapter._confirm_item_not_present(u'developers', u'maribel')
        self.assertRaises(ItemPresentError,
                          self.adapter._confirm_item_not_present, 
                          u'developers', u'linus')
    
    def test_checking_item_exclusion_in_non_existing_section(self):
        self.assertRaises(NonExistingSectionError,
                          self.adapter._confirm_item_is_present, u'users', 
                          u'linus')
