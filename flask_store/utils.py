# -*- coding: utf-8 -*-

"""
flask_store.utils
=================
"""


def path_to_uri(path):
    """ Swaps \\ for / Other stuff will happen here in the future.
    """

    return path.replace('\\', '/')
