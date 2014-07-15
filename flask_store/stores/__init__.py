# -*- coding: utf-8 -*-

"""
flask_store.stores
==================

Base store functionality and classes.
"""

import os
import tempfile
import time

from flask import current_app
from werkzeug.utils import secure_filename


class BaseStore(object):
    """ Base file storage class all storage providers should inherit from. This
    class provides some of the base functionality for all providers. Override
    as required.
    """

    def __init__(self, file_storage, destination=None):
        """ Constructor. When extending this class do not forget to call
        ``super``.

        This sets up base instance variables which can be used thoughtout the
        instance.

        Arguments
        ---------
        file_storage : werkzeug.datastructures.FileStorage
            The flask request file storage object

        Keyword Arguments
        -----------------
        destination : str, optional
            Relative destination directory, this is appended to the
            ``STORE_RELATIVE_BASE_PATH``, default None
        """

        # Base path which comes from application configuration, default the
        # the system file path seperator, e.g: /
        self.absolute_base_path = current_app.config['STORE_ABSOLUTE_BASE_PATH']

        # Relatvie path, this is used for storing a relative path in what
        # ever datbase you use jdefault the the system file path seperator,
        # e.g: /
        relative_base_path = current_app.config['STORE_RELATIVE_BASE_PATH']
        if relative_base_path.startswith(os.path.sep):
            relative_base_path = relative_base_path[1:]

        # Append the destination to the base relative path
        if destination:
            if destination.startswith(os.path.sep):
                destination = destination[1:]
            relative_base_path = os.path.join(relative_base_path, destination)

        # Save the relative base path
        self.relative_base_path = relative_base_path

        # Save the origional filename
        self.filename = file_storage.filename

        # Write the file to a temporary location on disk - this should be
        # cleaned up later - this allows us to upload the file even after the
        # request has finished so this could be co-routined with Gevent.
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.writelines(file_storage.stream)
            temp.flush()

        self.temp_file_path = temp.name

    def __exit__(self, type, value, traceback):
        """ Cleanup, deletes the temporary file from the file system.
        """

        os.unlink(self.temp_file_path)

    @property
    def safe_filename(self):
        """ If the file already exists the file will be renamed to contain a
        timestamp of when the file was created. This will avoid overwtites.

        Returns
        -------
        str
            A safe filenaem to use when writting the file
        """

        if not hasattr(self, '_safe_filename'):
            filename = self.filename
            while self.exists(filename):
                dir_name, file_name = os.path.split(filename)
                file_root, file_ext = os.path.splitext(file_name)
                timestamp = int(time.time())
                filename = secure_filename('{0}_{1}{2}'.format(
                    file_root,
                    timestamp,
                    file_ext))

            setattr(self, '_safe_filename', filename)

        return getattr(self, '_safe_filename')

    def absolute_dir_path(self):
        """ Returns the absolute path to the destination directory, this does
        not include the filename.

        Returns
        -------
        str
            Full **absolute** directory path.
        """

        return os.path.join(self.absolute_base_path, self.relative_base_path)

    def absolute_file_path(self, name=None):
        """ Returns the fulll absolute path to a file.

        Returns
        -------
        str
            Absolute path to the file
        """

        if name:
            filename = name
        else:
            filename = self.safe_filename

        return os.path.join(self.absolute_dir_path(), filename)

    def relative_dir_path(self):
        """ Returns the full relative directory path, this does not include the
        file name.

        Returns
        -------
        str
            Full **relative** directory path.
        """

        return self.relative_base_path

    def relative_file_path(self):
        """ Returns the full relative path to the file to be stored in some
        sort of database.

        Returns
        -------
        str
            Full **relative** path to file
        """

        return os.path.join(self.relative_dir_path(), self.safe_filename)

    def open_temp_file(self):
        """ Opens the temporary file.
        """

        return open(self.temp_file_path, 'rb')

    def exists(self):
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

    def save(self):
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
