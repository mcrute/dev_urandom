"""
Dictionary with Object-like Member Access
by Dan Buch (daniel.buch@gmail.com)
by Mike Crute (mcrute@gmail.com)

ObDict is a dictionary that has object-like access to its 
member items. The only difference between this and a regular
dict is that it will mangle names appropriately so that they
can be used for object-style access.
"""

from keyword import iskeyword
from warnings import warn


class ObDict(dict):
    """Dictionary with object-like member access
    """
    
    def __init__(self, *args):
        """Initialize the dictionary class.
        Calls the parent initializer then loops over the items in
        the object and cleans up the name. Calls get so nested 
        dicts will get converted to ObDicts as well.
        """
        super_ = super(self.__class__, self) # for brevity
        super_.__init__(*args)
        
        for key in self.keys():
            pretty = self._pretify(key)
            itemp = super_.__getitem__(key)
            del self[key]
            self[pretty] = itemp
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, 
                            super(self.__class__, self).__repr__())

    def get(self, key, default=None):
        """D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        try:
            return self._get(key)
        except KeyError:
            return default

    def _get(self, key):
        """Get with no default value option.
        Tests will fail if we rig the class magic methods up to the get
        with defaults so we have this to do the getting for those methods.
        """
        return super(self.__class__, self). \
                    __getitem__(self._pretify(key))

    def set(self, key, value):
        """Sets a value in the dictionary or an attribute
        Will set an item in the dictionary unless the attribute name 
        matches an actual attribute of the class. In which case will
        set that attribute.
        """
        super_ = super(self.__class__, self) # for brevity
        if hasattr(self, key):
            warn("The key %s is a class attribute, " \
                 "it will not be availiable to your dictionary." % key)
            super_.__setattr__(key, value)
        else:
            if isinstance(value, dict) and \
                not isinstance(value, self.__class__):
                value = self.__class__(value)
                
            super_.__setitem__(self._pretify(key), value)
            
    def _pretify(self, key):
        """Cleans up a variable name for use in object.
        Replaces any characters which are not legal in python attribute 
        names with the underscore character. If the name begins with a 
        number will prepend an underscore to the name. If the name is a
        python keyword will prepend an underscore to the name.
        """
        FORBIDDEN_CHARS = "[](){}#+$:;.,`~?!@\-*/%&|^=<> "
        key = "".join([k if k not in FORBIDDEN_CHARS else "_" for k in key])
        key = "%s_" % key if iskeyword(key) else key
        key = "_%s" % key if key[0].isdigit() else key
        return key
    
    #
    # INTERFACE CONFORMANCE (proxies to above functions)
    #
    def __getattr__(self, key):
        return self._get(key)

    def __setattr__(self, key, value):
        return self.set(key, value)
        
    def __getitem__(self, key):
        return self._get(key)
        
    def __setitem__(self, key, value):
        return self.set(key, value)