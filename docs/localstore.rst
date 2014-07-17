Local Store
===========

.. note::

    This document assumes you have already read the
    :doc:`quickstart` guide.

As we discussed in the :doc:`quickstart` guide Flask-Store uses its
:class:`flask_store.stores.local.LocalStore` as its default provider
and here we will discuss some of the more advanced concepts of this
store provider.

Enable
------

This is the default provider but if you wish to be explicit (+1) then
simply set the following in your application configuration::

    STORE_PROVIDER='flask_store.stores.local.LocalStore'

Configuration
-------------

The following configuration variables are available for you to customise.

+--------------------------------+-----------------------------------+
| Name                           | Example Value                     |
+================================+===================================+
| ``STORE_PATH``                 | ``/somewhere/on/disk``            |
+--------------------------------+-----------------------------------+
| This tells Flask-Store where to save uploaded files too. For this  |
| provider it must be an absolute path to a location on disk you     |
| have permission to write too. If the directory does not exist the  |
| provider will attempt to create the directory                      |
+--------------------------------+-----------------------------------+
| ``STORE_URL_PREFIX``           | ``/uploads``                      |
+--------------------------------+-----------------------------------+
| Used to generate the URL for the uploaded file. The ``LocalStore`` |
| will automatically register a route with your Flask application    |
| so the file can be accessed. Do not place domains in the path      |
| prefix.                                                            |
+--------------------------------+-----------------------------------+
