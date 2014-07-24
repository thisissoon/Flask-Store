# -*- coding: utf-8 -*-

"""
flask_store.providers.local
===========================

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
            provider = store.Provider(request.files.get('foo'))
            provider.save()

"""

import errno
import os

from flask_store.providers import Provider


class LocalProvider(Provider):
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

        # For Local file storage the default store path is the current
        # working directory
        app.config.setdefault('STORE_PATH', os.getcwdu())

        # Default URL Prefix
        app.config.setdefault('STORE_URL_PREFIX', '/uploads')

    def join(self, *parts):
        """ Joins paths together in a safe manor.

        Arguments
        ---------
        \*parts : list
            List of arbitrary paths to join together

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

    def save(self):
        """ Save the file on the local file system. Simply builds the paths
        and calls :meth:`werkzeug.datastructures.FileStorage.save` on the
        file object.
        """

        fp = self.fp
        filename = self.safe_filename(self.filename)
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
        fp.save(path)
        fp.close()

        # Update the filename - it may have changes
        self.filename = filename

    def open(self):
        """ Opens the file and returns the file handler.

        Returns
        -------
        file
            Open file handler
        """

        path = self.join(self.store_path, self.filename)
        try:
            fp = open(path, 'rb')
        except IOError:
            raise IOError('File does not exist: {0}'.format(self.absolute_path))

        return fp
