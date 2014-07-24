Quick Start
===========

Getting up and running with Flask-Store is pretty easy. By default Flask-Store
will use local file system storage to store your files. All you need to do is
to tell it where you want your uploaded files to live.

Step 1: Integration
-------------------

First lets initialise the Flask-Store extension with our Flask application
object.

.. sourcecode:: python

    from flask import Flask
    from flask.ext.store import Store

    app = Flask(__name__)
    store = Store(app)

    if __name__ == "__main__":
        app.run()

That is all there is to it. If you use an application factory then you can use
:meth:`flask_store.Store.init_app` method instead:

.. sourcecode:: python

    from flask import Flask
    from flask.ext.store import Store

    store = Store()

    def create_app():
        app = Flask(__name__)
        store.init_app(app)

    if __name__ == "__main__":
        app.run()

Step 2: Configuration
---------------------

So all we need to do now is tell Flask-Store where to save files once they have
been uploaded. For asolute url generation we also need to tell Flask-Store about
the domain where the files can accessed.

To do this we just need to set a configuration variable called ``STORE_PATH``
and ``STORE_DOMAIN``.

For brevity we will not show the application factory way because its pretty much
identical.

.. sourcecode:: python

    from flask import Flask
    from flask.ext.store import Store

    app = Flask(__name__)
    app.config['STORE_DOMAIN'] = 'http://127.0.0.1:5000'
    app.config['STORE_PATH'] = '/some/path/to/somewhere'
    store = Store(app)

    if __name__ == "__main__":
        app.run()

Now when Flask-Store saves a file it will be located here:
``/some/path/to/somewhere``.

Step 3: Add a route
--------------------

Now we just need to save a file. We just need a route which gets a file from the
request object and send it to our Flask-Store Provider (by default local
Storage) to save it.

.. note::

    It is important to note the Flask-Store makes no attempt to validate your
    file size, extensions or what not, it just does one thing and that is save
    files somewhere. So if you need validation you should use something like
    ``WTForms`` to validate incoming data from the user.

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

Now if we were to ``curl`` a file to our upload route we should get a url
back which tells how we can access it.

.. sourcecode:: bash

    curl -i -F afile=@localfile.jpg http://127.0.0.1:5000/upload

We should get back something like:

.. sourcecode:: http

    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Content-Length: 44
    Server: Werkzeug/0.9.6 Python/2.7.5
    Date: Thu, 17 Jul 2014 11:32:02 GMT

    http://127.0.0.1:5000/uploads/localfile.jpg%

Now if you went to ``http://127.0.0.1:5000/uploads/localfile.jpg`` in
your browser you should see the image you uploaded. That is because
Flask-Store automatically registers a route for serving files.

.. note::

    By the way, if you don't like the url you can change it by setting
    ``STORE_URL_PREFIX`` in your application configuration.

Step 4: There is no Step 4
--------------------------

Have a beer (or alcoholic beverage (or not) of your choice), that was
exhausting.
