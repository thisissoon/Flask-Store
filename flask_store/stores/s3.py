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

try:
    import boto
except ImportError:
    raise ImportError('boto must be installed to use the S3Store')


from flask import current_app
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

        aws_s3_region = current_app.config.get('STORE_AWS_S3_REGION')
        aws_access_key_id = current_app.config.get('STORE_AWS_ACCESS_KEY')
        aws_secret_access_key = current_app.config.get('STORE_AWS_SECRET_KEY')
        aws_bucket_name = current_app.config.get('STORE_AWS_S3_BUCKET')

        self.s3_connection = boto.s3.connect_to_region(
            aws_s3_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)

        self.bucket = self.s3_connection.get_bucket(aws_bucket_name)

        super(S3Store, self).__init__(*args, **kwargs)

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

        key = boto.s3.key.Key(
            name=self.absolute_file_path(name),
            bucket=self.bucket)

        return key.exists()

    def save(self):
        """ Takes the uploaded file and uploads it to s3.

        Returns
        -------
        str
            Relative path to file
        """

        key = self.bucket.new_key(self.absolute_file_path())
        key.set_metadata('Content-Type', self.file.mimetype)

        self.file.seek(0)

        key.set_contents_from_file(self.file)
        key.set_acl('public-read')
