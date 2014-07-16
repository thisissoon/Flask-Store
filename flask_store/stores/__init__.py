# -*- coding: utf-8 -*-

"""
flask_store.stores
==================

Base store functionality and classes.
"""

import os
import shortuuid

from flask import current_app
from werkzeug.utils import secure_filename


class BaseStore(object):
    """ Base file storage class all storage providers should inherit from. This
    class provides some of the base functionality for all providers. Override
    as required.
    """

    #: By default Stores do not require a route to be registered
    register_route = False

    def __init__(self, destination=None):
        """ Constructor. When extending this class do not forget to call
        ``super``.

        This sets up base instance variables which can be used thoughtout the
        instance.

        Keyword Arguments
        -----------------
        destination : str, optional
            Relative destination directory, this is appended to the
            ``STORE_RELATIVE_BASE_PATH``, default None
        """

        # Base path which comes from application configuration, default the
        # the system file path seperator, e.g: /
        self.store_path = current_app.config['STORE_PATH']

        # Append the destination to the base relative path
        if destination:
            if destination.startswith(os.path.sep):
                destination = destination[1:]
            self.store_path = os.path.join(self.store_path, destination)

        # Save Destination
        self.destination = destination

    def safe_filename(self, filename):
        """ If the file already exists the file will be renamed to contain a
        timestamp of when the file was created. This will avoid overwtites.

        Arguments
        ---------
        filename : str
            A filename to check if it exists

        Returns
        -------
        str
            A safe filenaem to use when writting the file
        """

        while self.exists(filename):
            dir_name, file_name = os.path.split(filename)
            file_root, file_ext = os.path.splitext(file_name)
            uuid = shortuuid.uuid()
            filename = secure_filename('{0}_{1}{2}'.format(
                file_root,
                uuid,
                file_ext))

        return filename

    def store_file_path(self, filename):
        """ Returns the fulll absolute path to a file.

        Arguments
        ---------
        filename : str
            Name of the file

        Returns
        -------
        str
            Absolute path to the file
        """

        return os.path.join(self.store_path, filename)

    def exists(self, *args, **kwargs):
        """ Placeholder "exists" method. This should be overridden by custom
        providers and return a ``boolean`` depending on if the file exists
        of not for the provider.

        Raises
        ------
        NotImplementedError
            If the "exists" method has not been implemented
        """

        raise NotImplementedError(
            'You must define an "exists" method in the {0} provider.'.format(
                self.__class__.__name__))

    def save(self, *args, **kwargs):
        """ Placeholder "sabe" method. This should be overridden by custom
        providers and save the file object to the provider.

        Raises
        ------
        NotImplementedError
            If the "save" method has not been implemented
        """

        raise NotImplementedError(
            'You must define an "save" method in the {0} provider.'.format(
                self.__class__.__name__))
