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

import errno
import os

from flask_store.stores import BaseStore


class LocalStore(BaseStore):

    def exists(self, name):
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

        return os.path.exists(self.absolute_file_path(name))

    def save(self):
        """ Save the file on the local file system. Simply builds the paths
        and calls :meth:`werkzeug.datastructures.FileStorage.save` on the
        file object.

        Returns
        -------
        str
            Relative path to file
        """

        absolute_path = self.absolute_dir_path
        directory = os.path.dirname(absolute_path)

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

        self.file.save(absolute_path)
