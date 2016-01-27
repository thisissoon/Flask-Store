``Flask-Store``
===============

``Flask-Store`` is a Flask Extension designed to provide easy file upload handling
in the same vien as Django-Storages, allowing developers to user custom storage
backends or one of the provided storage backends.

.. warning::

    This Flask Extenstion is under heavy development. It is likely API's will
    change over time but will be versioned so you can always stick to a version
    that works for you.

Example Usage
-------------

.. sourcecode:: python

    from flask import Flask, request
    from flask.ext.store import Store

    app = Flask(__name__)
    app.config['STORE_DOMAIN'] = 'http://127.0.0.1:5000'
    app.config['STORE_PATH'] = '/some/path/to/somewhere'
    store = Store(app)

    @app.route('/upload', methods=['POST', ])
    def upload():
        provider = store.Provider(request.files.get('afile'))
        provider.save()

        return provider.absolute_url

    if __name__ == "__main__":
        app.run()

Included Providers
------------------

* Local File System
* AWS Simple Storage Service (S3)
