# vim: set filencoding=utf8
"""
Implements Decorator

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 02, 2010

Used by:
    foundry
"""

def implements(interface, debug=False):
    """
    Verify that a class conforms to a specified interface.
    This decorator is not perfect, for example it can not
    check exceptions or return values. But it does ensure
    that all public methods exist and their arguments
    conform to the interface.

    The debug flag allows overriding checking of the runtime
    flag for testing purposes, it should never be set in
    production code.

    NOTE: This decorator does nothing if -d is not passed
    to the Python runtime.
    """
    import sys
    if not sys.flags.debug and not debug:
        return lambda func: func

    # Defer this import until we know we're supposed to run
    import inspect

    def get_filtered_members(item):
        "Gets non-private or non-protected symbols."
        return dict([(key, value) for key, value in inspect.getmembers(item)
                if not key.startswith('_')])

    def build_contract(item):
        """
        Builds a function contract string. The contract
        string will ignore the name of positional params
        but will consider the name of keyword arguments.
        """
        argspec = inspect.getargspec(item)

        if argspec.defaults:
            num_keywords = len(argspec.defaults)
            args = ['_'] * (len(argspec.args) - num_keywords)
            args.extend(argspec.args[num_keywords-1:])
        else:
            args = ['_'] * len(argspec.args)

        if argspec.varargs:
            args.append('*args')

        if argspec.keywords:
            args.append('**kwargs')

        return ', '.join(args)

    def tester(klass):
        "Verifies conformance to the interface."
        interface_elements = get_filtered_members(interface)
        class_elements = get_filtered_members(klass)

        for key, value in interface_elements.items():
            assert key in class_elements, \
                    "{0!r} is required but missing.".format(key)

            if inspect.isfunction(value) or inspect.ismethod(value):
                contract = build_contract(value)
                implementation = build_contract(class_elements[key])

                assert implementation == contract, \
                        "{0!r} doesn't conform to interface.".format(key)

        return klass

    return tester
