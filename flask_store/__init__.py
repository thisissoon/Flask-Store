# -*- coding: utf-8 -*-

"""
flask_store
===========

Adds simple file handling for different providers to your application. Provides
the following providers out of the box:

* Local file storeage
* Amazon Simple File Storage (requires ``boto`` to be installed)
"""

import os

from flask import current_app
from importlib import import_module
from werkzeug import LocalProxy


DEFAULT_PROVIDER = 'flask_store.stores.local.LocalStore'
StoreProvider = LocalProxy(lambda: store_provider())


def store_provider():
    """ Returns the default provider class as defined in the application
    configuration.

    Returns
    -------
    class
        The provider class
    """

    store = current_app.extensions['store']
    return store.store.Provider


class StoreState(object):
    """ Stores the state of Flask-Store from application init.
    """

    def __init__(self, store, app):
        self.store = store
        self.app = app


class Store(object):
    """ Flask-Store integration into Flask applications. Flask-Store can
    be integrated in two different ways depending on how you have setup your
    Flask application.

    You can bind to a specific flask application::

        app = Flask(__name__)
        store = Store(app)

    Or if you use an application factory you can use
    :meth:`flask_store.Store.init_app`::

        store = Store()
        def create_app():
            app = Flask(__name__)
            store.init_app(app)
            return app
    """

    def __init__(self, app=None):
        """ Constructor. Basically acts as a proxy to
        :meth:`flask_store.Store.init_app`.

        Key Arguments
        -------------
        app : flask.app.Flask, optional
            Optional Flask application instance, default None
        """

        if app:
            self.init_app(app)

    def init_app(self, app):
        """ Sets up application default confugration options and sets a
        ``Provider`` property which can be used to access the default
        provider class which handles the saving of files.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        app.config.setdefault('STORE_DEFAULT_PROVIDER', DEFAULT_PROVIDER)
        app.config.setdefault('STORE_ABSOLUTE_BASE_PATH', os.path.sep)
        app.config.setdefault('STORE_RELATIVE_BASE_PATH', os.path.sep)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['store'] = StoreState(self, app)

        self.Provider = self.provider(app)

    def provider(self, app):
        """ Fetches the provider class as defined by the application
        configuration.

        Raises
        ------
        ImportError
            If the class or module cannot be imported

        Returns
        -------
        class
            The provider class
        """

        if not hasattr(self, '_provider'):
            parts = app.config['STORE_DEFAULT_PROVIDER'].split('.')
            klass = parts.pop()
            path = '.'.join(parts)

            module = import_module(path)
            if not hasattr(module, klass):
                raise ImportError('{0} provider not found at {1}'.format(
                    klass,
                    path))

            self._provider = getattr(module, klass)

        return getattr(self, '_provider')
