# -*- coding: utf-8 -*-

"""
flask_store.exceptions
======================

Custom Flask-Store exception classes.
"""


class NotConfiguredError(Exception):
    """ Raise this exception in the event the flask application has not been
    configured properly.
    """

    pass
