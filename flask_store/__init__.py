# -*- coding: utf-8 -*-

"""
flask_store
===========

Adds simple file handling for different providers to your application. Provides
the following providers out of the box:

* Local file storeage
* Amazon Simple File Storage (requires ``boto`` to be installed)
"""

# Python 2/3 imports
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from flask import current_app, send_from_directory
from flask_store.exceptions import NotConfiguredError
from importlib import import_module
from werkzeug.local import LocalProxy


DEFAULT_PROVIDER = 'flask_store.providers.local.LocalProvider'
Provider = LocalProxy(lambda: store_provider())


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

        app.config.setdefault('STORE_DOMAIN', None)
        app.config.setdefault('STORE_PROVIDER', DEFAULT_PROVIDER)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['store'] = StoreState(self, app)

        # Set the provider class
        self.Provider = self.provider(app)

        # Set configuration defaults based on provider
        self.set_provider_defaults(app)

        # Ensure that any required configuration vars exist
        self.check_config(app)

        # Register a flask route - the provider must have register_route = True
        self.register_route(app)

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
            parts = app.config['STORE_PROVIDER'].split('.')
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

        def serve(filename):
            return send_from_directory(app.config['STORE_PATH'], filename)

        # Only do this if the Provider says so
        if self.Provider.register_route:
            url = urlparse.urljoin(
                app.config['STORE_URL_PREFIX'].lstrip('/') + '/',
                '<path:filename>')
            app.add_url_rule('/' + url, 'flask.store.file', serve)
