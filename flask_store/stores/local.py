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
    app.config['STORE_ABSOLUTE_BASE_PATH'] = '/some/file/path'
    app.config['STORE_RELATIVE_BASE_PATH'] = '/uploads'

    store = Store(app)

    @app,route('/upload')
    def upload():
        form = FooForm()
        form.validate_on_submit()

        if not form.errors:
            store = Provider(request.files.get('foo'))
            store.save()

"""

import os

from flask_store.stores import BaseStore


class LocalStore(BaseStore):

    def save(self):
        """ Save the file on the local file system. Simply builds the paths
        and calls :meth:`werkzeug.datastructures.FileStorage.save` on the
        file object.

        Returns
        -------
        str
            Relative path to file
        """

        if not os.path.isdir(self.absolute_dir_path):
            raise IOError('{0} is not a directory'.format(
                self.absolute_dir_path))

        self.file.save(self.absolute_file_path)

        return self.relative_file_path
