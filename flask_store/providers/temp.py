# -*- coding: utf-8 -*-

"""
flask_store.providers.temp
==========================
"""

import tempfile

from flask_store.providers.local import LocalProvider


class TemporaryStore(LocalProvider):
    """
    """

    def save(self, file):
        """
        """

        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.writelines(file)
            temp.flush()

        return temp.name
