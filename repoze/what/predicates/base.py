# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
Base definitions for predicate checkers.

"""

from webob import Request

__all__ = ['Predicate', 'CompoundPredicate', 'NotAuthorizedError']


#{ Base classes for predicate checkers


class Predicate(object):
    """
    Generic predicate checker.
    
    This is the base predicate class. It won't do anything useful for you, 
    unless you subclass it.
    
    """
    
    def __init__(self, msg=None):
        """
        Create a predicate and use ``msg`` as the error message if it fails.
        
        :param msg: The error message, if you want to override the default one
            defined by the predicate.
        :type msg: str
        
        You may use the ``msg`` keyword argument with any predicate.
        
        """
        if msg:
            self.message = msg
    
    def evaluate(self, userid, request, helpers):
        """
        Raise an exception if the predicate is not met.
        
        :param userid: The current user's identifier (if authenticated) as
            a short-cut.
        :type userid: basestring or None
        :param request: The WebOb ``Request`` object for the current request.
        :type request: :class:`webob.Request`
        :param helpers: The :mod:`repoze.what` ``helpers`` dictionary
            as a short-cut.
        :type helpers: dict
        :raise NotImplementedError: When the predicate doesn't define this
            method.
        :raises NotAuthorizedError: If the predicate is not met (use 
            :meth:`unmet` to raise it).
        
        This is the method that must be overridden by any predicate checker.
        
        For example, if your predicate is "The current month is the specified
        one", you may define the following predicate checker::
        
            from datetime import date
            from repoze.what.predicates.base import Predicate
            
            class is_month(Predicate):
                message = 'The current month must be %(right_month)s'
                
                def __init__(self, right_month, **kwargs):
                    self.right_month = right_month
                    super(is_month, self).__init__(**kwargs)
                
                def evaluate(self, userid, request, helpers):
                    today = date.today()
                    if today.month != self.right_month:
                        # Raise an exception because the predicate is not met.
                        self.unmet()
        
        .. attention::
            Do not evaluate predicates by yourself using this method. See
            :meth:`check_authorization`.

        .. warning::
        
            To make your predicates thread-safe, keep in mind that they may
            be instantiated at module-level and then shared among many threads,
            so avoid predicates from being modified after their evaluation. 
            This is, the ``evaluate()`` method should not add, modify or 
            delete any attribute of the predicate.
        
        """
        raise NotImplementedError
    
    def unmet(self, msg=None, **placeholders):
        """
        Raise an exception because this predicate is not met.
        
        :param msg: The error message to be used; overrides the predicate's
            default one.
        :type msg: str
        :raises NotAuthorizedError: All the time.
        
        ``placeholders`` represent the placeholders for the predicate message.
        The predicate's attributes will also be taken into account while
        creating the message with its placeholders.
        
        For example, if you have a predicate that checks that the current
        month is the specified one, where the predicate message is defined with
        two placeholders as in::
        
            The current month must be %(right_month)s and it is %(this_month)s
        
        and the predicate has an attribute called ``right_month`` which
        represents the expected month, then you can use this method as in::
        
            self.unmet(this_month=this_month)
        
        Then :meth:`unmet` will build the message using the ``this_month``
        keyword argument and the ``right_month`` attribute as the placeholders
        for ``this_month`` and ``right_month``, respectively. So, if
        ``this_month`` equals ``3`` and ``right_month`` equals ``5``,
        the message for the exception to be raised will be::
        
            The current month must be 5 and it is 3
        
        If you have a context-sensitive predicate checker and thus you want
        to change the error message on evaluation, you can call :meth:`unmet`
        as::
        
            self.unmet('%(this_month)s is not a good month',
                       this_month=this_month)
        
        The exception raised would contain the following message::
        
            3 is not a good month
        
        .. attention::
        
            This method should only be called from :meth:`evaluate`.
        
        """
        if msg:
            message = msg
        else:
            message = self.message
        # Let's convert it into unicode because it may be just a class, as a 
        # Pylons' "lazy" translation message:
        message = unicode(message)
        # Include the predicate attributes in the placeholders:
        all_placeholders = self.__dict__.copy()
        all_placeholders.update(placeholders)
        raise NotAuthorizedError(message % all_placeholders)
    
    def check_authorization(self, environ):
        """
        Evaluate the predicate and raise an exception if it's not met.
        
        :param environ: The WSGI environment.
        :raise NotAuthorizedError: If it the predicate is not met.
        
        Example::
        
            >>> from repoze.what.predicates.user import is_user
            >>> environ = gimme_the_environ()
            >>> p = is_user('gustavo')
            >>> p.check_authorization(environ)
            # ...
            repoze.what.predicates.base.NotAuthorizedError: The current user must be "gustavo"
        
        """
        logger = environ.get('repoze.what.logger')
        userid, request, helpers = self._parse_environ(environ)
        try:
            self.evaluate(userid, request, helpers)
        except NotAuthorizedError, error:
            logger and logger.info(u'Authorization denied: %s' % error)
            raise
        logger and logger.info('Authorization granted')

    def is_met(self, environ):
        """
        Find whether the predicate is met or not.
        
        :param environ: The WSGI environment.
        :return: Whether the predicate is met or not.
        :rtype: bool
        
        Example::
        
            >>> from repoze.what.predicates.user import is_user
            >>> environ = gimme_the_environ()
            >>> p = is_user('gustavo')
            >>> p.is_met(environ)
            False
        
        """
        userid, request, helpers = self._parse_environ(environ)
        try:
            self.evaluate(userid, request, helpers)
            return True
        except NotAuthorizedError:
            return False
    
    def _parse_environ(self, environ):
        """
        Extract the userid, the :mod:`repoze.what` ``helpers`` dict and the
        :mod:`WebOb` ``Request`` object from the WSGI ``environ`` dict.
        
        """
        return (environ['repoze.what.userid'], Request(environ),
                environ['repoze.what.helpers'])


class CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    
    def __init__(self, *predicates, **kwargs):
        super(CompoundPredicate, self).__init__(**kwargs)
        self.predicates = predicates


#{ Exceptions


class NotAuthorizedError(Exception):
    """
    Exception raised by :meth:`Predicate.check_authorization` if a
    subject is not allowed to access the requested source.
    
    """
    pass


#}
