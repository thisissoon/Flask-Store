class BaseStore(object):
    """ Base file storage class all storage backends should inherit from.
    """

    def save(self):
        pass

    def delete(self):
        pass

    def exists(self):
        pass
