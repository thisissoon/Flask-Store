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

    def save(self):
        """
        """

        fp = self.fp
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.writelines(fp)
            temp.flush()

        return temp.name
