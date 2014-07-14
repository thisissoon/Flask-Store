# -*- coding: utf-8 -*-

"""
flask_store.stores
==================

Base store functionality and classes.
"""

import os
import time

from flask import current_app
from werkzeug.utils import secure_filename


class BaseStore(object):
    """ Base file storage class all storage backends should inherit from.
    """

    def __init__(self, file, destination=None):
        """ Constructor. When extending this class do not forget to call
        ``super``.

        This sets up base instance variables which can be used thoughtout the
        instance.

        Arguments
        ---------
        file : werkzeug.datastructures.FileStorage
            The uploaded file object which is part of the request, this could
            also take a file like object.

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
        self.relative_base_path = relative_base_path

        # Store the file object on the instance
        self.file = file

        # Store the destination on the instance
        self.destination = destination

    @property
    def filename(self):
        """ If the file already exists the file will be renamed to contain a
        timestamp of when the file was created. This will avoid overwtites.

        Returns
        -------
        str
            A safe filenaem to use when writting the file
        """

        if not hasattr(self, '_filename'):
            filename = self.file.filename
            while self.exists(filename):
                dir_name, file_name = os.path.split(filename)
                file_root, file_ext = os.path.splitext(file_name)
                timestamp = int(time.time())
                filename = secure_filename('{0}_{1}{2}'.format(
                    file_root,
                    timestamp,
                    file_ext))

            setattr(self, '_filename', filename)

        return getattr(self, '_filename')

    def absolute_dir_path(self):
        """ Returns the absolute path to the destination directory, this does
        not include the filename.

        Returns
        -------
        str
            Full **absolute** directory path.
        """

        parts = [self.absolute_base_path, self.relative_base_path, ]
        if not self.destination:
            parts.append(self.destination)

        return os.path.join(*parts)

    def absolute_file_path(self, filename=None):
        """ Returns the fulll absolute path to a file.

        Keyword Arguments
        -----------------
        name : str, optional
            Optional file name to join with the absolure directory path

        Returns
        -------
        str
            Absolute path to the file
        """

        if not filename:
            filename = self.filename

        return os.path.join(self.absolute_dir_path(), filename)

    def relative_dir_path(self):
        """ Returns the full relative directory path, this does not include the
        file name.

        Returns
        -------
        str
            Full **relative** directory path.
        """

        parts = [self.relative_base_path, ]
        if self.destination:
            parts.append(self.destination)

        return os.path.join(*parts)

    def relative_file_path(self):
        """ Returns the full relative path to the file to be stored in some
        sort of database.

        Returns
        -------
        str
            Full **relative** path to file
        """

        return os.path.join(self.relative_dir_path(), self.filename)

    def exists(self):
        raise NotImplementedError(
            'You must define an "exists" method in the {0} provider.'.format(
                self.__class__.__name__))

    def save(self):
        pass

    def delete(self):
        pass
