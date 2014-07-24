# -*- coding: utf-8 -*-

"""
flask_store.utils
=================
"""

import os


def path_to_uri(path):
    """ Swaps \\ for / Other stuff will happen here in the future.
    """

    return path.replace('\\', '/')


def is_path(f):
    """ Determines if the passed argument is a string or not, if is a string
    it is assumed to be a path. Taken from Pillow, all credit goes to the Pillow
    / PIL team.

    Arguments
    ---------
    f
        Could be anything

    Returns
    -------
    bool
        Is a string or not
    """

    if bytes is str:
        return isinstance(f, basestring)
    else:
        return isinstance(f, (bytes, str))


def is_directory(f):
    """ Checks if an object is a string, and that it points to a directory.
    Taken from Pillow, all credit goes to the Pillow / PIL team.

    Arguments
    ---------
    f
        Could be anything

    Returns
    -------
    bool
        Is a path to a directory or not
    """

    return is_path(f) and os.path.isdir(f)
