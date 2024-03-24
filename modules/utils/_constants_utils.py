class Struct(object):
    def __init__(self, *args):
        """
        Constructor for the Struct class.
        - Initializes the Struct with a header if provided.
        Parameters:
            - *args: Variable length argument list, the first argument is used as the header.
        """
        self.__header__ = str(args[0]) if args else None

    def __repr__(self):
        """
        Representation method for the Struct.
        - Returns a string representation of the Struct.
        - If a header is set, it returns the header; otherwise, it returns the default object
            representation.
        """
        if self.__header__ is None:
            return super(Struct, self).__repr__()
        return self.__header__

    def next(self):
        """
        Fake iteration functionality.
        - Raises StopIteration to simulate the behavior of an iterator.
        - This method is a placeholder and does not provide actual iteration functionality.
        """
        raise StopIteration

    def __iter__(self):
        """
        Custom iterator for the Struct.
        - Iterates over the attributes of the Struct instance.
        - Skips magic attributes (those starting with '__') and attributes that are instances of Struct.
        Yields:
            - Yields the values of the non-magic, non-Struct attributes of the instance.
        """
        ks = self.__dict__.keys()
        for k in ks:
            if not k.startswith("__") and not isinstance(k, Struct):
                yield getattr(self, k)

    def __len__(self):
        """
        Length method for the Struct.
        - Calculates the number of non-magic, non-Struct attributes in the Struct.
        Returns:
            - (int): The number of relevant attributes in the Struct instance.
        """
        ks = self.__dict__.keys()
        return len(
            [k for k in ks if not k.startswith("__") and not isinstance(k, Struct)]
        )