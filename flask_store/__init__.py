# -*- coding: utf-8 -*-

"""
flask_store
===========

Flask-Store extension can be created from here using the standard Flask
extension convention.

Example
-------
.. sourcecode:: python

    >>> from flask import Flask
    >>> from flask.ext.store import Store
    >>> app = Flask(__name__)
    >>> store = Store(app)

    # Or

    >>> from flask import Flask
    >>> from flask.ext.store import Store
    >>> app = Flask(__name__)
    >>> store = Store()
    >>> store.init_app(app)
"""

from importlib import import_module
from flask import current_app
from werkzeug import LocalProxy


CONFIG_REQUIRED = [
    'STORE_BASE_PATH',
    'STORE_RELATIVE_PATH']


Backend = LocalProxy(lambda: get_store_backend())


def get_store_backend():
    if not hasattr(current_app, 'store_default_backend'):
        raise NotImplementedError(
            'You must instantiate Flask-Store when creating your application')

    return getattr(current_app, 'store_default_backend')


class Store(object):

    def __init__(self, app=None):
        if app:
            self.app = app
            self.construct()

    def init_app(self, app):
        self.app = app
        self.construct()

    def construct(self):
        self.validate_configuration()
        default_store = self.app.config.get(
            'STORE_DEFAULT_BACKEND',
            'flask_store.stores.local.LocalStore')

        parts = default_store.split('.')
        kls_name = parts.pop()
        module_path = '.'.join(parts)

        module = import_module(module_path)
        if not getattr(module, kls_name):
            raise ImportError('{0} class not found in {1}'.format(
                kls_name,
                module_path))

        self.app.store_default_backend = getattr(module, kls_name)

    def validate_configuration(self):
        """ Validate the Flask Application Configuration to ensure that
        the user has configured the required settings.

        Raises
        ------
        NotImplementedError
            In the event a required configuration option is missing
        """

        for name in CONFIG_REQUIRED:
            if name not in self.app.config:
                raise NotImplementedError(
                    '{0} must be set in your Flask Application '
                    'Configuration'.format(name))
