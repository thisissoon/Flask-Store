# -*- coding: utf-8 -*-

"""
flask_store.stores.local
========================

Local file storage for your Flask application.

Example
-------

.. sourcecode:: python

    from flask import Flask, request
    from flask.ext.store import Provider, Store
    from wtforms import Form
    from wtforms.fields import FileField

    class FooForm(Form):
        foo = FileField('foo')

    app = Flask(__app__)
    app.config['STORE_PATH'] = '/some/file/path'

    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        if not form.errors:
            provider = store.Provider()
            provider.save(request.files.get('foo'))


"""

import errno
import os

from flask_store.stores import BaseStore
from flask_store.files import StoreFile


class LocalStore(BaseStore):
    """ The default provider for Flask-Store. Handles saving files onto the
    local file system.
    """

    #: Ensure a route is registered for serving files
    register_route = True

    @staticmethod
    def app_defaults(app):
        """ Sets sensible application configuration settings for this
        provider.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application at init
        """

        app.config.setdefault('STORE_PATH', os.getcwdu())
        app.config.setdefault('STORE_URL_PREFIX', '/flaskstore')

    def join(self, *parts):
        """ Joins paths together in a safe manor.

        Returns
        -------
        str
            Joined paths
        """

        path = ''
        for i, part in enumerate(parts):
            if i > 0:
                part = part.lstrip(os.path.sep)
            path = os.path.join(path, part)

        return path.rstrip(os.path.sep)

    def exists(self, filename):
        """ Returns boolean of the provided filename exists at the compiled
        absolute path.

        Arguments
        ---------
        name : str
            Filename to check its existence

        Returns
        -------
        bool
            Whether the file exists on the file system
        """

        path = self.join(self.store_path, filename)
        return os.path.exists(path)

    def save(self, file):
        """ Save the file on the local file system. Simply builds the paths
        and calls :meth:`werkzeug.datastructures.FileStorage.save` on the
        file object.

        See Also
        --------

        Arguments
        ---------
        file : werkzeug.datastructures.FileStorage
            The file uploaded by the user

        Returns
        -------
        flask_store.file_wapper.FileWrapper
            A thin wrapper around the file and provider
        """

        filename = self.safe_filename(file.filename)
        path = self.join(self.store_path, filename)
        directory = os.path.dirname(path)

        if not os.path.exists(directory):
            # Taken from Django - Race condition between os.path.exists and
            # os.mkdirs
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        if not os.path.isdir(directory):
            raise IOError('{0} is not a directory'.format(directory))

        # Save the file
        file.save(path)
        file.close()

        # Returns a file wrapper instance around the file and provider
        return StoreFile(filename, destination=self.destination)
