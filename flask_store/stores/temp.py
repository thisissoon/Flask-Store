# -*- coding: utf-8 -*-

"""
flask_store.stores.temp
=======================
"""

import tempfile

from flask_store.stores import BaseStore


class TemporaryStore(BaseStore):
    """
    """

    def save(self, file):
        """
        """

        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.writelines(file)
            temp.flush()

        return temp.name
