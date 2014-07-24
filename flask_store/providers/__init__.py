# -*- coding: utf-8 -*-

"""
flask_store.providers
=====================

Base store functionality and classes.
"""

import os
import shortuuid
import urlparse

from flask import current_app
from flask_store.utils import is_path, path_to_uri
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class Provider(object):
    """ Base provider class all storage providers should inherit from. This
    class provides some of the base functionality for all providers. Override
    as required.
    """

    #: By default Providers do not require a route to be registered
    register_route = False

    def __init__(self, fp, location=None):
        """ Constructor. When extending this class do not forget to call
        ``super``.

        This sets up base instance variables which can be used thoughtout the
        instance.

        Arguments
        ---------
        fp : werkzeug.datastructures.FileStorage, str
            A FileStorage instance or absolute path to a file

        Keyword Arguments
        -----------------
        location : str, optional
            Relative location directory, this is appended to the
            ``STORE_PATH``, default None
        """

        # The base store path for the provider
        self.store_path = self.join(current_app.config['STORE_PATH'])

        # Save the fp - could be a FileStorage instance or a path
        self.fp = fp

        # Get the filename
        if is_path(fp):
            self.filename = os.path.basename(fp)
        else:
            if not isinstance(fp, FileStorage):
                raise ValueError(
                    'File pointer must be an instance of a '
                    'werkzeug.datastructures.FileStorage')
            self.filename = fp.filename

        # Save location
        self.location = location

        # Appends location to the store path
        if location:
            self.store_path = self.join(self.store_path, location)

    @property
    def relative_path(self):
        """ Returns the relative path to the file, so minus the base
        path but still includes the location if it is set.

        Returns
        -------
        str
            Relative path to file
        """

        parts = []
        if self.location:
            parts.append(self.location)
        parts.append(self.filename)

        return self.join(*parts)

    @property
    def absolute_path(self):
        """ Returns the absollute file path to the file.

        Returns
        -------
        str
            Absolute file path
        """

        return self.join(self.store_path, self.filename)

    @property
    def relative_url(self):
        """ Returns the relative URL, basically minus the domain.

        Returns
        -------
        str
            Realtive URL to file
        """

        parts = [current_app.config['STORE_URL_PREFIX'], ]
        if self.location:
            parts.append(self.location)
        parts.append(self.filename)

        return path_to_uri(self.url_join(*parts))

    @property
    def absolute_url(self):
        """ Absolute url contains a domain if it is set in the configuration,
        the url predix, location and the actual file name.

        Returns
        -------
        str
            Full absolute URL to file
        """

        if not current_app.config['STORE_DOMAIN']:
            path = self.relative_url

        path = urlparse.urljoin(
            current_app.config['STORE_DOMAIN'],
            self.relative_url)

        return path_to_uri(path)

    def safe_filename(self, filename):
        """ If the file already exists the file will be renamed to contain a
        short url safe UUID. This will avoid overwtites.

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

    def url_join(self, *parts):
        """ Safe url part joining.

        Arguments
        ---------
        \*parts : list
            List of parts to join together

        Returns
        -------
        str
            Joined url parts
        """

        path = ''
        for i, part in enumerate(parts):
            if i > 0:
                part = part.lstrip('/')
            path = urlparse.urljoin(path.rstrip('/') + '/', part.rstrip('/'))

        return path.lstrip('/')

    def join(self, *args, **kwargs):
        """ Each provider needs to implement how to safely join parts of a
        path together to result in a path which can be used for the provider.

        Raises
        ------
        NotImplementedError
            If the "join" method has not been implemented
        """

        raise NotImplementedError(
            'You must define a "join" method in the {0} provider.'.format(
                self.__class__.__name__))

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
            'You must define a "exists" method in the {0} provider.'.format(
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
            'You must define a "save" method in the {0} provider.'.format(
                self.__class__.__name__))
