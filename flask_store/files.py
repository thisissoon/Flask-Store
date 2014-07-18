# -*- coding: utf-8 -*-

"""
flask_store.files
=================
"""

import urlparse

from flask import current_app
from flask_store import StoreProvider
from flask_store.utils import path_to_uri


class StoreFile(object):
    """ An Ambassador class for the provider for a specific file. Each
    method basically proxies to methods on the provider.
    """

    def __init__(self, filename, destination=None):
        """ Sets up the provider.

        Arguments
        ---------
        filename : str
            Name of the file, not the full or relative

        Keyword Arguments
        -----------------
        destination : str, optional
            An extra path prefix, default ``None``
        """

        # Set the provider to be the provider defined in application
        # configuration
        self.provider = StoreProvider(destination=destination)

        # Save the name of the file
        self.filename = filename

    def absolute_path(self):
        """ Returns the absollute file path to the file.

        Returns
        -------
        str
            Absolute file path
        """

        return self.provider.join(self.provider.store_path, self.filename)

    def relative_path(self):
        """ Returns the relative path to the file, so minus the base
        path but still includes the destination if it is set.

        Returns
        -------
        str
            Relative path to file
        """

        parts = []
        if self.provider.destination:
            parts.append(self.provider.destination)
        parts.append(self.filename)

        return self.provider.join(*parts)

    def absolute_url(self):
        """ Absolute url contains a domain if it is set in the configuration,
        the url predix, destination and the actual file name.

        Returns
        -------
        str
            Full absolute URL to file
        """

        if not current_app.config['STORE_DOMAIN']:
            path = self.relative_url()

        path = urlparse.urljoin(
            current_app.config['STORE_DOMAIN'],
            self.relative_url())

        return path_to_uri(path)

    def relative_url(self):
        """ Returns the relative URL, basically minus the domain.

        Returns
        -------
        str
            Realtive URL to file
        """

        parts = [current_app.config['STORE_URL_PREFIX'], ]
        if self.provider.destination:
            parts.append(self.provider.destination)
        parts.append(self.filename)

        return path_to_uri(self.provider.url_join(*parts))
