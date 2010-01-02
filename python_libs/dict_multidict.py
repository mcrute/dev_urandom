class MultiDict(dict):
    """
    An ordered dictionary that can have multiple values for each key.
    Adds the methods getall, getone, mixed, and add to the normal
    dictionary interface.
    """

    def __init__(self, *args, **kwargs):
        if args:
            if hasattr(args[0], 'iteritems'):
                self.update(arg[0])
            else:
                for key, value in args[0]:
                    self.add(key, value)
        if kwargs:
            self.update(kwargs)

    @classmethod
    def fromkeys(cls, keys, defaults=None):
        return cls(dict([(key, defaults) for key in keys]))

    def __getitem__(self, key):
        return dict.__getitem__(self, key)[-1]

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, [value])

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.items())

    def add(self, key, value):
        """
        Add the key and value, not overwriting any previous value.
        """
        if key not in self:
            self[key] = value
        else:
            dict.__getitem__(self, key).append(value)

    def getall(self, key):
        """
        Return a list of all values matching the key (may be an empty list)
        """
        return dict.get(self, key, [])

    def getone(self, key):
        """
        Get one value matching the key, raising a KeyError if multiple
        values were found.
        """
        value = dict.__getitem__(self, key)
        if len(value) > 1:
            raise ValueError
        return value[0]

    def mixed(self):
        """
        Returns a dictionary where the values are either single
        values, or a list of values when a key/value appears more than
        once in this dictionary.  This is similar to the kind of
        dictionary often used to represent the variables in a web
        request.
        """
        output = {}
        for key, value in dict.iteritems(self):
            if len(value) == 1:
                output[key] = value[0]
            else:
                output[key] = value
        return output

    def dict_of_lists(self):
        """
        Returns a dictionary where each key is associated with a
        list of values.
        """
        output = {}
        for key, value in dict.iteritems(self):
            output[key] = value
        return

    def copy(self):
        return self.__class__(self)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self.get(key, default)

    def update(self, other=None, **kwargs):
        if hasattr(other, 'keys'):
            for key in other.keys():
                self.add(key, other[key])
        else:
            for key, value in other:
                self.add(key, value)

        if kwargs:
            self.update(kwargs)

    def items(self):
        output = []
        for key, value in dict.iteritems(self):
            for item in value:
                output.append((key, item))
        return output

    def iteritems(self):
        for key, value in dict.iteritems(self):
            for item in value:
                yield (key, item)

    def values(self):
        output = []
        for value in dict.itervalues(self):
            output.extend(value)
        return output

    def itervalues(self):
        for value in dict.itervalues(self):
            for item in value:
                yield item

__test__ = {
    'general': """
    >>> d = MultiDict(a=1, b=2)
    >>> d['a']
    1
    >>> d.getall('c')
    []
    >>> d.add('a', 2)
    >>> d['a']
    2
    >>> d.getall('a')
    [1, 2]
    >>> d['b'] = 4
    >>> d.getall('b')
    [4]
    >>> d.keys()
    ['a', 'b']
    >>> d.items()
    [('a', 1), ('a', 2), ('b', 4)]
    >>> d.mixed() == {'a': [1, 2], 'b': 4}
    True
    >>> MultiDict([('a', 'b')], c=2)
    MultiDict([('a', 'b'), ('c', 2)])
    """}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

