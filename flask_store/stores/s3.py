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
    app.config['STORE_DEFAULT_BACKEND'] = 'flask_store.stores.s3.S3Store'
    app.config['STORE_AWS_ACCESS_KEY'] = 'foo'
    app.confog['STORE_AWS_SECRET_KEY'] = 'bar'

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
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    warnings.warn('Gevent is not installed, you will not be able to use the '
                  'S3GreenStore')

import mimetypes
import os

try:
    import boto
except ImportError:
    raise ImportError('boto must be installed to use the S3Store/S3GreenStore')


from flask import copy_current_request_context, current_app
from flask_store.stores import BaseStore


class S3Store(BaseStore):

    REQUIRED_CONFIGURATION = [
        'STORE_AWS_ACCESS_KEY',
        'STORE_AWS_SECRET_KEY',
        'STORE_AWS_S3_BUCKET',
        'STORE_AWS_S3_REGION']

    def __init__(self, *args, **kwargs):
        """ Initiates connection to AWS S3 and gets the bucket.
        """

        super(S3Store, self).__init__(*args, **kwargs)

        self.aws_s3_region = current_app.config.get('STORE_AWS_S3_REGION')
        self.aws_access_key_id = current_app.config.get('STORE_AWS_ACCESS_KEY')
        self.aws_secret_access_key = \
            current_app.config.get('STORE_AWS_SECRET_KEY')
        self.aws_bucket_name = current_app.config.get('STORE_AWS_S3_BUCKET')

    def connect(self):
        """ Returns an S3 connection instance.
        """

        if not hasattr(self, '_s3connection'):
            s3connection = boto.s3.connect_to_region(
                self.aws_s3_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key)
            setattr(self, '_s3connection', s3connection)
        return getattr(self, '_s3connection')

    def bucket(self, s3connection):
        """ Returns an S3 bucket instance
        """

        return s3connection.get_bucket(self.aws_bucket_name)

    def exists(self, name):
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

        key = boto.s3.key.Key(
            name=self.absolute_file_path(name),
            bucket=bucket)

        return key.exists()

    def save(self):
        """ Takes the uploaded file and uploads it to s3.

        Returns
        -------
        str
            Relative path to file
        """

        s3connection = self.connect()
        bucket = self.bucket(s3connection)
        temp_file = self.open_temp_file()

        key = bucket.new_key(self.absolute_file_path())
        key.set_contents_from_file(temp_file)

        mimetype, encoding = mimetypes.guess_type(self.filename)
        key.set_metadata('Content-Type', mimetype)
        key.set_acl('public-read')

        temp_file.close()
        os.unlink(self.temp_file_path)

        return self.relative_file_path()


class S3GeventStore(S3Store):
    """ A Gevent Support version of :class:`.S3Store`. Calling :meth:`.save`
    here will spawn a greenlet which will handle the actual upload process.
    """

    def save(self):
        """ Acts as a proxy to the actual save method in the parent class. The
        save method will be called in a ``greenlet`` so ``gevent`` must be
        installed.

        Returns
        -------
        str
            Relative path to file
        """

        @copy_current_request_context
        def _save():
            super(S3GeventStore, self).save()

        gevent.spawn(_save)

        return self.relative_file_path()
