# -*- coding: utf-8 -*-

"""
flask_store.providers.s3
========================

AWS Simple Storage Service file Store.

Example
-------
.. sourcecode:: python

    from flask import Flask, request
    from flask.ext.Store import Provider, Store
    from wtforms import Form
    from wtforms.fields import FileField

    class FooForm(Form):
        foo = FileField('foo')

    app = Flask(__app__)
    app.config['STORE_PROVIDER'] = 'flask_store.providers.s3.S3Provider'
    app.config['STORE_S3_ACCESS_KEY'] = 'foo'
    app.confog['STORE_S3_SECRET_KEY'] = 'bar'

    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        provider = Provider(form.files.get('foo'))
        provider.save()
"""

try:
    import boto
    BOTO_INSTALLED = True
except ImportError:
    BOTO_INSTALLED = False

try:
    import gevent.monkey
    gevent.monkey.patch_all()
    GEVENT_INSTALLED = True
except ImportError:
    GEVENT_INSTALLED = False

# Standard Libs
import io
import mimetypes
import os

# Third Party Libs
from flask import copy_current_request_context, current_app
from flask_store.exceptions import NotConfiguredError
from flask_store.providers import Provider
from flask_store.providers.temp import TemporaryStore
from werkzeug.datastructures import FileStorage


class S3Provider(Provider):
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

        # For S3 by default the STORE_PATH is the root of the bucket
        app.config.setdefault('STORE_PATH', '/')

        # For S3 the STORE_PATH makes up part of the key and therefore
        # doubles up as the STORE_URL_PREFIX
        app.config.setdefault('STORE_URL_PREFIX', app.config['STORE_PATH'])

        # Default ACL
        # http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        app.config.setdefault('STORE_S3_ACL', 'private')

        if not BOTO_INSTALLED:
            raise ImportError(
                'boto must be installed to use the S3Provider or the '
                'S3GeventProvider')

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
        \*parts : list
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

    def save(self):
        """ Takes the uploaded file and uploads it to S3.

        Note
        ----
        This is a blocking call and therefore will increase the time for your
        application to respond to the client and may cause request timeouts.
        """

        fp = self.fp
        s3connection = self.connect()
        bucket = self.bucket(s3connection)
        filename = self.safe_filename(self.filename)
        path = self.join(self.store_path, filename)
        mimetype, encoding = mimetypes.guess_type(filename)

        fp.seek(0)

        key = bucket.new_key(path)
        key.set_metadata('Content-Type', mimetype)
        key.set_contents_from_file(fp)
        key.set_acl(current_app.config.get('STORE_S3_ACL'))

        # Update the filename - it may have changes
        self.filename = filename

    def open(self):
        """ Opens an S3 key and returns an oepn File Like object pointer.

        Returns
        -------
        _io.BytesIO
            In memory file data
        """

        s3connection = self.connect()
        bucket = self.bucket(s3connection)
        key = bucket.get_key(self.relative_path)

        if not key:
            raise IOError('File does not exist: {0}'.format(self.relative_path))

        return io.BytesIO(key.read())  # In memory


class S3GeventProvider(S3Provider):
    """ A Gevent Support for :class:`.S3Provider`. Calling :meth:`.save`
    here will spawn a greenlet which will handle the actual upload process.
    """

    def __init__(self, *args, **kwargs):
        """
        """

        if not GEVENT_INSTALLED:
            raise NotConfiguredError(
                'You must have gevent installed to use the S3GeventProvider')

        super(S3GeventProvider, self).__init__(*args, **kwargs)

    def save(self):
        """ Acts as a proxy to the actual save method in the parent class. The
        save method will be called in a ``greenlet`` so ``gevent`` must be
        installed.

        Since the origional request will close the file object we write the
        file to a temporary location on disk and create a new
        :class:`werkzeug.datastructures.FileStorage` instance with the stram
        being the temporary file.
        """

        fp = self.fp
        temp = TemporaryStore(fp)
        path = temp.save()
        filename = self.safe_filename(fp.filename)

        @copy_current_request_context
        def _save():
            self.fp = FileStorage(
                stream=open(path, 'rb'),
                filename=filename,
                name=fp.name,
                content_type=fp.content_type,
                content_length=fp.content_length,
                headers=fp.headers)

            super(S3GeventProvider, self).save()

            # Cleanup - Delete the temp file
            os.unlink(path)

        gevent.spawn(_save)

        self.filename = filename
