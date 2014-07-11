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
    app.config['STORE_BASE_PATH'] = '/'
    app.config['STORE_RELATIVE_PATH'] = 'uploads'

    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        backend = Backend()
        backend.save(form.files.get('foo'))
"""

import os

try:
    from boto.s3.connection import S3Connection
except ImportError:
    raise ImportError('boto must be installed to use the S3Store')

from flask import current_app as app
from flask_store.stores import BaseStore
from werkzeug.utils import secure_filename


class S3Store(BaseStore):

    def __init__(self):
        self.conn = S3Connection(
            app.config.get('STORE_AWS_ACCESS_KEY'),
            app.config.get('STORE_AWS_SECRET_KEY'))

        self.root_path = app.config.get(
            'STORE_BASE_PATH')
        self.relative_path = app.config.get(
            'STORE_RELATIVE_PATH')

    def save(self, file, to=None):
        relative_path = os.path.join(
            self.relative_path,
            secure_filename(file.filename))
        full_path = os.path.join(self.root_path, relative_path)

        bucket = self.conn.get_bucket(app.config.get('STORE_AWS_S3_BUCKET'))

        key = bucket.new_key(full_path)
        key.set_metadata('Content-Type', file.mimetype)
        file.stream.seek(0)
        key.set_contents_from_file(file.stream)
        key.set_acl('public-read')
