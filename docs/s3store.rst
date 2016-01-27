S3 Store
========

.. note::

    This document assumes you have already read the
    :doc:`quickstart` guide.

The S3 Store allows you to forward your uploaded files up to an AWS
Simple Storage Service (S3) bucket. This takes the problem of storing large
numbers of files away from you onto Amazon.

.. note::

    Amazon's ``boto`` is required. Boto is not included as a install
    requirement for Flask-Store as not  everyone will want to use the S3
    provider. To install just run::

        pip install boto

Enable
------

To use this provider simply set the following in your application
configuration::

    STORE_PROVIDER='flask_store.providers.s3.S3Provider'

Configuration
-------------

The following configuration variables are availible to you.

+----------------------------+---------------------------------------+
| Name                       | Example Value                         |
+============================+=======================================+
| ``STORE_PATH``             |  ``/some/place/in/bucket``            |
+----------------------------+---------------------------------------+
| For the ``S3Provider`` is basically your key name prefix rather    |
| than an actual location. So for the example value above the key    |
| for a file might be: ``/some/place/in/bucket/foo.jpg``             |
+----------------------------+---------------------------------------+
| ``STORE_DOMAIN``           | ``https://bucket.s3.amazonaws.com``   |
+----------------------------+---------------------------------------+
| Your S3 bucket domain, this is used to generate an absolute url.   |
+----------------------------+---------------------------------------+
| ``STORE_S3_REGION``        | ``us-east-1``                         |
+----------------------------+---------------------------------------+
| The region in which your bucket lives                              |
+----------------------------+---------------------------------------+
| ``STORE_S3_BUCKET``        | ``your.bucket.name``                  |
+----------------------------+---------------------------------------+
| The name of the S3 bucket to upload files too                      |
+----------------------------+---------------------------------------+
| ``STORE_S3_ACCESS_KEY``    | ``ABCDEFG12345``                      |
+----------------------------+---------------------------------------+
| Your AWS access key which has permission to upload files to the    |
| ``STORE_S3_BUCKET``.                                               |
+----------------------------+---------------------------------------+
| ``STORE_S3_SECRET_KEY``    | ``ABCDEFG12345``                      |
+----------------------------+---------------------------------------+
| Your AWS access secret key                                         |
+--------------------------------------------------------------------+
| ``STORE_S3_ACL``           | ``public-read``                       |
+----------------------------+---------------------------------------+
| ACL to set uploaded files, defaults to ``private``, see S3_ACL_    |
+----------------------------+---------------------------------------+

.. _S3_ACL: http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl

S3 Gevent Store
===============

.. note::

    This document assumes you have already read the
    :doc:`quickstart` guide.

The :class:`flask_store.providers.s3.S3GeventProvider` allows you to run the
upload to S3 process in a Gevent Greenlet process. This allows your webserver
to send a response back to the client whilst the upload to S3 happends in
the background.

Obviously this means that when the request has finished the upload may not have
finished and the key not exist in the bucket. You will need to build your
application around this.

.. note::

    The ``gevent`` package is required. Gevent is not included as a install
    requirement for Flask-Store as not everyone will want to use the S3 Gevent
    provider. To install just run::

        pip install gevent

Enable
------

To use this provider simply set the following in your application
configuration::

    STORE_PROVIDER='flask_store.providers.s3.S3GeventProvider'

Configuration
-------------

.. note::

    This is a sub class of :class:`flask_store.providers.s3.S3Provider` and
    therefore all the same confiuration options apply.
