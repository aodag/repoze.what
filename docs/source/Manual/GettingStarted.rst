***************************************
Getting started with :mod:`repoze.what`
***************************************



Terminology
-----------

Because you may store your groups and permissions where you would like to, not
only in a database, :mod:`repoze.what` uses a generic terminology:

.. glossary::

    source
        Where authorization data (groups and/or permissions) is stored.
        It may be a database or a file (an Htgroups file, an Ini file, etc), for
        example.
    sources
        See :term:`source`.
    group source
        A :term:`source` that stores groups. For example, an Htgroups
        file or an Ini file.
    permission source
        A :term:`source` that stores permissions. For example, an
        Ini file.
    source adapter
        An object that manages a given type of :term:`source` to add,
        edit and delete entries under an API independent of the source type.
    adapter
        See :term:`source adapter`.
    adapters
        See :term:`source adapter`.
    group adapter
        An :term:`adapter` that deals with one :term:`group source`.
    permission adapter
        An :term:`adapter` that deals with one :term:`permission source`.
    section
        Sections are the groups that make up a source -- this is, in a
        `permission source`, the sections are the permissions, and in a `group
        source`, the sections are the groups.
    item
        The elements that are contained in a :term:`section`. In a
        :term:`permission source`, the items are the groups that are granted
        the permission represented in their parent section; likewise, in a
        :term:`group source`, the items are the Ids of the users that belong to
        the group represented in the parent section.


The authentication framework (:mod:`repoze.who`) only deals with the 
:term:`source` (or sources) that handle your users' credentials, while the 
authorization framework (:mod:`repoze.what`) deals with both the 
source(s) that handle your groups and those that handle your permissions.

Sample sources
~~~~~~~~~~~~~~

Below are the contents of a mock ``.htgroups`` file that defines the groups of
an application. In other words, such a file is a :term:`group source` of
type ``htgroups``::

    developers: rms, linus, guido
    admins: rms, linus
    users: gustavo, maribel

It has three sections and five items: "developers" (made up of the items "rms",
"linus" and "guido"), "admins" (made up of the items "rms" and "linus") and
"users (made up of the items "gustavo" and "maribel").

And below are the contents of a mock ``.ini`` file that defines the permissions
of the groups in an application. In other words, such a file is a
:term:`permission source` of type ``Ini``::

    [manage-site]
    admins
    [release-software]
    admins
    developers
    [contact-us]
    users

It has four sections and three items: "manage-site" (made up one item,
"admins"), "release-software" (made up of the items "admins" and "developers")
and "contact-us" (made up of the item "users").

If you use a database to store your users, groups and permissions, then such a
database is both the group and permission source:

  * The tables where you store your groups and users are the sections and the
    section items, respectively, of the ``group source``.
  * The tables where you store your permissions and groups are the sections and
    the section items, respectively, of the ``permission source``.


.. _add-auth-middleware:

Setting up authentication and authorization
-------------------------------------------

To enable authorization in your Web application, you need to add some
WSGI middleware to your application, which is automatically done for you if
you are using the quickstart (:mod:`repoze.what.plugins.quickstart`).

When you enable authorization with :mod:`repoze.what`, authentication
with :mod:`repoze.who` is automatically enabled.

.. note::
    The `quickstart` is enabled when in ``{yourproject}.config.app_cfg`` you
    have ``base_config.auth_backend`` set. To disable it, it's enough to
    remove that line -- and you may also want to delete those like
    ``base_config.sa_auth.*``.


Using authentication and authorization without the quickstart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're not using the quickstart, then you have to add the required
middleware in your application. This gives you more flexibility, such as being
able not to use a database to store your users' credentials, your groups
and/or your permissions.

You are highly encouraged to add such a middleware with a function defined in,
say, ``{yourproject}.config.middleware`` and called, say, ``add_auth``. Then
such a function may look like this::

    def add_auth(app, config):
        from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check
        from repoze.what.middleware import setup_auth
        # Please note that the plugins below have not been created yet; want to
        # jump in?
        from repoze.what.plugins.htgroups import HtgroupsAdapter
        from repoze.what.plugins.ini import IniPermissionAdapter

        # Defining the group adapters; you may add as much as you need:
        groups = {'all_groups': HtgroupsAdapter('/path/to/groups.htgroups')}

        # Defining the permission adapters; you may add as much as you need:
        permissions = {'all_perms': IniPermissionAdapter('/path/to/perms.ini')}

        # repoze.who authenticators; you may add as much as you need:
        htpasswd_auth = HTPasswdPlugin('/path/to/users.htpasswd', crypt_check)
        authenticators = [('htpasswd', htpasswd_auth)]

        app_with_auth = setup_auth(
            app,
            config,
            groups,
            permissions,
            authenticators)
        return app_with_auth

Of course, there are other things you may customize, such as adding
:mod:`repoze.who` identifiers, more authenticators, challengers and metadata
providers -- read on!

Now you're ready to add the middleware. Go to ``{yourproject}.config.middleware``
and edit ``make_auth`` to make it look like this::

    def make_app(global_conf, full_stack=True, **app_conf):
        app = make_base_app(global_conf, full_stack=True, **app_conf)
        # Wrap your base turbogears app with custom middleware
        app = add_auth(app, config)
        return app


What's next?
------------

Once your application includes the required WSGI middleware for authentication
and authorization, as explained in :ref:`add-auth-middleware`, you are ready
to implement authorization in your controllers with
:mod:`repoze.what.authorize`.