# -*- coding: utf-8 -*-

"""
flask_store.sqlalchemy
======================

Custom SQLAlchemy types for handling Flask-Store instances in SQLAlchemy.
"""


try:
    import sqlalchemy
    SQLALCHEMY_INSTALLED = True
except ImportError:
    SQLALCHEMY_INSTALLED = False


from flask_store import Provider
from flask_store.exceptions import NotConfiguredError
from werkzeug.datastructures import FileStorage


class FlaskStoreType(sqlalchemy.types.TypeDecorator):
    """ A SQL Alchemy custom type which will save a file using the Flask
    Application Configured Store Provider and saves the relative path the the
    database.

    Also creates a fresh provider instance when accessing the data attribute
    from an instance.

    Example
    -------
    .. sourcecode:: python

        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_store import Store
        from flask_store.sqla import FlaskStoreType

        app = Flask(__name__)

        db = SQLAlchemy(app)
        store = Store(app)

        class MyModel(db.Model):
            field = db.Column(FlaskStoreType(location='/some/place'))
    """

    #: Implements a standard unicode type
    impl = sqlalchemy.Unicode(256)

    def __init__(self, max_length=256, location=None, *args, **kwargs):
        """ Contructor, sets the location of the file relative from the
        base path.
        """

        if not SQLALCHEMY_INSTALLED:
            raise NotConfiguredError(
                'You need to install sqlalchemy to use the FlaskStoreType')

        self.location = location

        super(FlaskStoreType, self).__init__(*args, **kwargs)
        self.impl = sqlalchemy.types.Unicode(max_length)

    def process_bind_param(self, value, dialect):
        """ Called when setting the value be stored in the database field, this
        will be the files relative file path.

        Arguments
        ---------
        value : werkzeug.datastructures.FileStorage
            The uploaded file to save
        dialect : sqlalchemy.engine.interfaces.Dialect
            The dialect

        Returns
        -------
        str
            The files realtive path on what ever storage backend defined in the
            Flask Application configuration
        """

        if not isinstance(value, FileStorage):
            return None

        provider = Provider(value, location=self.location)
        provider.save()

        return provider.relative_path

    def process_result_value(self, value, dialect):
        """ Called when accessing the value from the database and returning the
        appropriate provider file wrapper.

        Arguments
        ---------
        value : str
            The stored relative path in the database
        dialect : sqlalchemy.engine.interfaces.Dialect
            The dialect

        Returns
        -------
        obj
            An instance of the Store Provider class
        """

        provider = Provider(value, location=self.location)
        return provider
