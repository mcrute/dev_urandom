"""
__version__
__author__
__date__
"""

PYTHON_PATH = "/Users/cruteme/Desktop/ag_python_lib/"

import compiler
from pprint import pprint as pretty_print
from compiler import visitor, consts, ast

class ASTVisitor(visitor.ASTVisitor, object):
    """
    Lets make this a snazzy new-style class.
    """
    pass

class ShallowASTVisitor(ASTVisitor):
    """
    Shallow AST visitors operate only on modules and consider
    only the first level of the tree (thus, they are shallow).
    """

    def default(self, node, *args):
        if isinstance(node, ast.Module):
            node = node.node.nodes
        else:
            raise ValueError("Shallow visitor can only visit modules.")

        for child in node:
            self.dispatch(child, *args)


class ShallowSymbolVisitor(ShallowASTVisitor):
    """
    Attempt to get all publically accessible module-level
    symbols from a module. These are things that someone
    could import.

    NOTE: This doesn't consider imports, those are considered
    to be virtual symbols and handled by a different visitor.
    """

    def __init__(self):
        self.public_symbols = set()
        self.private_symbols = set()
        self.protected_symbols = set()
        self.magic_symbols = set()
        ASTVisitor.__init__(self)

    def visitClass(self, node):
        self._put_in_set(node.name)

    def visitAssign(self, node):
        first_child = node.nodes[0]

        if isinstance(first_child, ast.AssName):
            self._put_in_set(first_child.name)
        elif isinstance(first_child, ast.AssTuple):
            for item in first_child.nodes:
                self._put_in_set(item.name)

    def visitFunction(self, node):
        self._put_in_set(node.name)

    def visitAssName(self, node):
        if node.flags is consts.OP_DELETE:
            self._remove_from_set(node.name)

    def visitAssTuple(self, node):
        for item in node.nodes:
            if (isinstance(item, ast.AssName) and 
                    item.flags is consts.OP_DELETE):
                self._remove_from_set(item.name)

    def _remove_from_set(self, symbol_name):
        protection = get_protection_status(symbol_name)

        try:
            if protection is SYMBOL_PRIVATE:
                self.private_symbols.remove(symbol_name)
            elif protection is SYMBOL_MAGIC:
                self.magic_symbols.remove(symbol_name)
            elif protection is SYMBOL_PROTECTED:
                self.protected_symbols.remove(symbol_name)
            elif protection is SYMBOL_PUBLIC:
                self.public_symbols.remove(symbol_name)
        except KeyError:
            """Some values might not exist because they came
            from imports."""
            pass

    def _put_in_set(self, symbol_name):
        protection = get_protection_status(symbol_name)

        if protection is SYMBOL_PRIVATE:
            self.private_symbols.add(symbol_name)
        elif protection is SYMBOL_MAGIC:
            self.magic_symbols.add(symbol_name)
        elif protection is SYMBOL_PROTECTED:
            self.protected_symbols.add(symbol_name)
        elif protection is SYMBOL_PUBLIC:
            self.public_symbols.add(symbol_name)

    @property
    def all_symbols(self):
        return (self.private_symbols | self.public_symbols |
                self.protected_symbols | self.magic_symbols)


SYMBOL_PRIVATE = "SYMBOL_PRIVATE"
SYMBOL_PROTECTED = "SYMBOL_PROTECTED"
SYMBOL_PUBLIC = "SYMBOL_PUBLIC"
SYMBOL_MAGIC = "SYMBOL_MAGIC"

def get_protection_status(symbol_name):
    if symbol_name.startswith("__") and not symbol_name.endswith("__"):
        return SYMBOL_PRIVATE
    elif symbol_name.startswith("__") and symbol_name.endswith("__"):
        return SYMBOL_MAGIC
    elif symbol_name.startswith("_"):
        return SYMBOL_PROTECTED
    else:
        return SYMBOL_PUBLIC


class ImportVisitor(ASTVisitor, object):

    def __init__(self):
        self.symbols = {}
        super(ImportVisitor, self).__init__()

    def visitImport(self, node):
        for name in node.names:
            self.put_symbol(name[0])

    def visitFrom(self, node):
        symbols = []
        for symbol, _ in node.names:
            symbols.append(symbol)
        self.put_symbol(node.modname, symbols)

    def put_symbol(self, module, symbols=None):
        if not symbols:
            symbols = set()
    
        if not isinstance(symbols, set):
            symbols = set(symbols)
    
        if module not in self.symbols:
            self.symbols[module] = symbols
        else:
            self.symbols[module] |= symbols

    @property
    def modules(self):
        return self.symbols.keys()


def get_exported_symbols(ast_tree):
    virtual_symbols = get_virutal_symbols(ast_tree)


def get_real_symbols(ast_tree):
    pass


def get_virtual_symbols(ast_tree):
    """
    Virtual symbols are those symbols which are imported
    by the module but not really defined by the module.
    """
    import_visitor = ImportVisitor()
    visitor.walk(ast_tree, import_visitor)
    
    virtual_symbols = import_visitor.symbols.values()
    virtual_symbols = set(flatten_nested_list(virtual_symbols))

    return virtual_symbols


def get_private_symbols(ast_tree):
    pass


def flatten_nested_list(list_):
    output = []
    
    for item in list_:
        if isinstance(item, (set, tuple, list)):
            output += flatten_nested_list(item)
        else:
            output.append(item)

    return output


is_empty_set = lambda input_: input_ == set()

def warn_about_module(symbol_table):
    required_tags = set(["__date__", "__author__", "__version__"])
    if not required_tags.issubset(symbol_table.magic_symbols):
        print "*** Missing magic metainfo tags!"

    if is_empty_set(symbol_table.public_symbols):
        print "*** Module exports no pubilc non-virtual symbols!"

    if (is_empty_set(symbol_table.public_symbols) and
            not is_empty_set(symbol_table.virtual_symbols)):
        print "*** Module exports only virtual symbols."


def main():
    #tree = compiler.parseFile(PYTHON_PATH + "app/view/widget/widget.py")
    #tree = compiler.parseFile(PYTHON_PATH + "app/yhm/yhmcardorderpage.py")
    tree = compiler.parseFile(PYTHON_PATH + "app/ag/beta/wire.py")
    #tree = compiler.parseFile("/Library/Python/2.5/site-packages/SQLAlchemy-0.5.0beta1-py2.5.egg/sqlalchemy/__init__.py")
    #tree = compiler.parseFile("/Users/cruteme/Desktop/test.py")

    visitor_ = ShallowSymbolVisitor()
    visitor_.virtual_symbols = get_virtual_symbols(tree)
    visitor.walk(tree, visitor_)

    print "Public Symbols:"
    print visitor_.public_symbols
    print ""
    print "Private Symbols:"
    print visitor_.private_symbols
    print ""
    print "Protected Symbols:"
    print visitor_.protected_symbols
    print ""
    print "Magic Symbols:"
    print visitor_.magic_symbols
    print ""
    print "Virtual Symbols:"
    print visitor_.virtual_symbols

    print ""
    warn_about_module(visitor_)

if __name__ == "__main__":
    main()
