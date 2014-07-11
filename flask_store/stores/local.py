# -*- coding: utf-8 -*-

"""
flask_store.stores.local
========================

Local file store.

Example
-------
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
    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        backend = Backend()
        backend.save(form.files.get('foo'))

"""

import os

from flask import current_app as app
from flask_store.stores import BaseStore
from werkzeug.utils import secure_filename


class LocalStore(BaseStore):

    def __init__(self):
        self.root_path = app.config.get(
            'STORE_BASE_PATH')
        self.relative_path = app.config.get(
            'STORE_RELATIVE_PATH')

    def save(self, file):
        """ Save the file on the local file system.

        Arguments
        ---------
        werkzeug_file : werkzeug.datastructures.FileStorage
            The raw data of the file

        Keyword Arguments
        -----------------
        to : str, optional
            The destination directory where the file should live, this
            is a relative file path, not the absolute path, default ``None``
        """

        relative_path = os.path.join(
            self.relative_path,
            secure_filename(file.filename))
        dir_path = os.path.join(self.root_path, self.relative_path)
        full_path = os.path.join(self.root_path, relative_path)

        if not os.path.isdir(dir_path):
            raise Exception('Not a directory')

        file.save(full_path)

        return relative_path
