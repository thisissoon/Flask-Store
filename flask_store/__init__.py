# -*- coding: utf-8 -*-

"""
flask_store
===========

Adds simple file handling for different providers to your application. Provides
the following providers out of the box:

* Local file storeage
* Amazon Simple File Storage (requires ``boto`` to be installed)
"""

from flask import current_app, send_from_directory
from flask_store.exceptions import NotConfiguredError
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

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['store'] = StoreState(self, app)

        self.Provider = self.provider(app)
        self.check_config(app)
        self.set_provider_defaults(app)

    def check_config(self, app):
        """ Checks the required application configuration variables are set
        in the flask application.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance

        Raises
        ------
        NotConfiguredError
            In the event a required config parameter is required by the
            Store.
        """

        if hasattr(self.Provider, 'REQUIRED_CONFIGURATION'):
            for name in self.Provider.REQUIRED_CONFIGURATION:
                if not app.config.get(name):
                    raise NotConfiguredError(
                        '{0} must be configured in your flask application '
                        'configuration'.format(name))

    def provider(self, app):
        """ Fetches the provider class as defined by the application
        configuration.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance

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

    def set_provider_defaults(self, app):
        """ If the provider has a ``app_defaults`` static method then this
        simply calls that method. This will set sensible application
        configuration options for the provider.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        if hasattr(self.Provider, 'app_defaults'):
            self.Provider.app_defaults(app)

    def register_route(self, app):
        """ Registers a default route for serving uploaded assets via
        Flask-Store, this is based on the absolute and relative paths
        defined in the app configuration.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        def serve(self, path):
            return send_from_directory(
                app.config['STORE_PATH'],
                path)

        # Only do this if the Provider says so
        if self.Provider.register_route:
            app.add_url_rule('', 'flask.store.file', serve)
