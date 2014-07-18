# -*- coding: utf-8 -*-

"""
flask_store.stores.s3
=====================

AWS Simple Storage Service file Store.

Example
-------
.. sourcecode:: python

    from flask import Flask, request
    from flask.ext.Store import Backend, Store
    from wtforms import Form
    from wtforms.fields import FileField

    class FooForm(Form):
        foo = FileField('foo')

    app = Flask(__app__)
    app.config['STORE_PROVIDER'] = 'flask_store.stores.s3.S3Store'
    app.config['STORE_S3_ACCESS_KEY'] = 'foo'
    app.confog['STORE_S3_SECRET_KEY'] = 'bar'

    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        backend = Backend()
        backend.save(form.files.get('foo'))
"""

import warnings

try:
    import boto
    BOTO_INSTALLED = True
except ImportError:
    BOTO_INSTALLED = False

try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    warnings.warn('Gevent is not installed, you will not be able to use the '
                  'S3GreenStore')

import mimetypes
import os

from flask import copy_current_request_context, current_app
from flask_store.stores import BaseStore
from flask_store.files import StoreFile
from flask_store.stores.temp import TemporaryStore
from werkzeug.datastructures import FileStorage


class S3Store(BaseStore):
    """ Amazon Simple Storage Service Store (S3). Allows files to be stored in
    an AWS S3 bucket.
    """

    #: Required application configuration variables
    REQUIRED_CONFIGURATION = [
        'STORE_S3_ACCESS_KEY',
        'STORE_S3_SECRET_KEY',
        'STORE_S3_BUCKET',
        'STORE_S3_REGION']

    @staticmethod
    def app_defaults(app):
        """ Sets sensible application configuration settings for this
        provider.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application at init
        """

        app.config.setdefault('STORE_PATH', '/')
        app.config.setdefault('STORE_URL_PREFIX', '')

        if not BOTO_INSTALLED:
            raise ImportError('boto must be installed to use the '
                              'S3Store/S3GreenStore')

    def connect(self):
        """ Returns an S3 connection instance.
        """

        if not hasattr(self, '_s3connection'):
            s3connection = boto.s3.connect_to_region(
                current_app.config['STORE_S3_REGION'],
                aws_access_key_id=current_app.config['STORE_S3_ACCESS_KEY'],
                aws_secret_access_key=current_app.config['STORE_S3_SECRET_KEY'])
            setattr(self, '_s3connection', s3connection)
        return getattr(self, '_s3connection')

    def bucket(self, s3connection):
        """ Returns an S3 bucket instance
        """

        return s3connection.get_bucket(
            current_app.config.get('STORE_S3_BUCKET'))

    def join(self, *parts):
        """ Joins paths into a url.

        Arguments
        ---------
        *parts : list
            List of arbitrary paths to join together

        Returns
        -------
        str
            S3 save joined paths
        """

        return self.url_join(*parts)

    def exists(self, filename):
        """ Checks if the file already exists in the bucket using Boto.

        Arguments
        ---------
        name : str
            Filename to check its existence

        Returns
        -------
        bool
            Whether the file exists on the file system
        """

        s3connection = self.connect()
        bucket = self.bucket(s3connection)
        path = self.join(self.store_path, filename)

        key = boto.s3.key.Key(name=path, bucket=bucket)

        return key.exists()

    def save(self, file):
        """ Takes the uploaded file and uploads it to S3.

        Note
        ----
        This is a blocking call and therefore will increase the time for your
        application to respond to the client and may cause request timeouts.

        Arguments
        ---------
        file : werkzeug.datastructures.FileStorage
            The file uploaded by the user

        Returns
        -------
        str
            Relative path to file
        """

        s3connection = self.connect()
        bucket = self.bucket(s3connection)
        filename = self.safe_filename(file.filename)
        path = self.join(self.store_path, filename)
        mimetype, encoding = mimetypes.guess_type(filename)

        file.seek(0)

        key = bucket.new_key(path)
        key.set_metadata('Content-Type', mimetype)
        key.set_contents_from_file(file)
        key.set_acl('public-read')

        file.close()

        # Returns a file wrapper instance around the file and provider
        return StoreFile(filename, destination=self.destination)


class S3GeventStore(S3Store):
    """ A Gevent Support for :class:`.S3Store`. Calling :meth:`.save`
    here will spawn a greenlet which will handle the actual upload process.
    """

    def save(self, file):
        """ Acts as a proxy to the actual save method in the parent class. The
        save method will be called in a ``greenlet`` so ``gevent`` must be
        installed.

        Since the origional request will close the file object we write the
        file to a temporary location on disk and create a new
        :class:`werkzeug.datastructures.FileStorage` instance with the stram
        being the temporary file.

        Returns
        -------
        str
            Relative path to file
        """

        temp = TemporaryStore()
        path = temp.save(file)
        filename = self.safe_filename(file.filename)

        @copy_current_request_context
        def _save():
            storage = FileStorage(
                stream=open(path, 'rb'),
                filename=filename,
                name=file.name,
                content_type=file.content_type,
                content_length=file.content_length,
                headers=file.headers)

            super(S3GeventStore, self).save(storage)

            # Cleanup - Delete the temp file
            os.unlink(path)

        gevent.spawn(_save)

        # Returns a file wrapper instance around the file and provider
        return StoreFile(filename, destination=self.destination)
