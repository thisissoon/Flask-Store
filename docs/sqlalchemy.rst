SQLAlchemy
==========

If you use SQLAlchemy to store data in a database you can take advantage of the
bundled :class:`flask_store.sqla.FlaskStoreType` which will take a lot of the
cruft away for you.

.. note::

    In the following examples we are assuming you have your application
    setup using the application factory pattern. We will also not
    show the application factory method.

Model
-----

As normal you would use Flask-SQLAlchemy to define your model but you would use
the :class:`flask_store.sqla.FlaskStoreType` type when defining the field type
for the field you want to store the file path too.

.. sourcecode:: python

    from flask_store.sqla import FlaskStoreType
    from yourapp.ext import db

    class MyModel(db.Model):
        field = db.Column(FlaskStoreType(128, location='/some/where'))

This will act as a standard unicode string field. You do not need to pass a
``max_length`` integer as we have here as this will default to ``256``.

The ``location`` keyword argument we have passed as an optional **relative**
path to where your file should be saved too from the ``STORE_PATH`` defined
in your Flask Application Configuration as described in the :doc:`quickstart`
guide.

Saving
------

When wanting to save the file you just need to set the attribute to be the
instance of the request file uploaded, this will save the file to the location.

.. sourcecode:: python

    from yourapp import create_app
    from yourapp.ext import db
    from yourapp.models import MyModel

    app = create_app()

    @route('/foo')
    def foo():
        foo = MyModel()
        foo.field = request.files.get('foo')

        db.session.add(foo)
        db.session.commit()

        return foo.absolute_url

Accessing
---------

When accessing an object the relative path stored in the database will be
automatically converted to a store provider instance. This will give you access
to the object:

.. sourcecode:: python

    from yourapp import create_app
    from yourapp.ext import db
    from yourapp.models import MyModel

    app = create_app()

    @route('/bar')
    def foo():
        foo = MyModel.query.get(1)

        return foo.absolute_url
