"""
ObDict Test Suite
by Dan Buch (daniel.buch@gmail.com)
by Mike Crute (mcrute@gmail.com)

ObDict is a dictionary that has object-like access to its 
member items. The only difference between this and a regular
dict is that it will mangle names appropriately so that they
can be used for object-style access.
"""

import unittest
from obdict import ObDict


class TestObDict(unittest.TestCase):
    
    def setUp(self):
        self.empty_obdict = ObDict()
        self.full_obdict = ObDict({ "some": "stuff" })
        self.obdict_test = ObDict({ "some": "item", "somes": { "other": "item" }, "0borked": "val", "some!legal;": "val2"})
    
    def test_pretify_fixes_leading_numeral(self):
        assert self.empty_obdict._pretify("0borked") == "_0borked"
        
    def test_pretify_doesnt_fix(self):
        assert self.empty_obdict._pretify("b0rked") == "b0rked"
        
    def test_pretify_fixes_keywords(self):
        assert self.empty_obdict._pretify("assert") == "assert_"
        
    def test_pretify_fixes_illegals(self):
        assert self.empty_obdict._pretify("th!s;sb4d") == "th_s_sb4d"
    
    def test_repr(self):
        assert repr(self.full_obdict) == "ObDict({'some': 'stuff'})"
        
    def test_init_fixes_names(self):
        assert "some" in self.obdict_test
        assert "somes" in self.obdict_test
        
        assert "_0borked" in self.obdict_test
        assert "0borked" not in self.obdict_test
        
        assert "some_legal_" in self.obdict_test
        assert "some!legal;" not in self.obdict_test
        
    def test_get_gets_stuff(self):
        assert self.obdict_test.get("some") == "item"
        assert self.obdict_test.get("_0borked") == "val"
        assert self.obdict_test.get("some_legal_") == "val2"
        
    def test_get_gets_default(self):
        assert self.obdict_test.get("superman", "kryptonite") == "kryptonite"
        
    def test_set_sets_values(self):
        self.obdict_test.set("test_stuff", "superman")
        assert "test_stuff" in self.obdict_test
        assert self.obdict_test["test_stuff"] == "superman"
        
    def test_set_recursively_creates_obdicts(self):
        my_obdict = ObDict({ "sub1": { "some": "stuff" }, "sub2": { "more": { "stuff": "inhere" }}})
        
        assert isinstance(my_obdict["sub1"], ObDict)
        assert isinstance(my_obdict["sub2"], ObDict)
        assert isinstance(my_obdict["sub2"]["more"], ObDict)
        
    def test_get_set_with_subscripts(self):
        self.full_obdict["blah"] = "canhaz?"
        assert self.full_obdict["blah"] == "canhaz?"
        
    def test_get_set_with_oject_notation(self):
        self.full_obdict.blah = "canhaz?"
        assert self.full_obdict.blah == "canhaz?"
    
    def test_set_sets_attributes(self):
        self.empty_obdict.from_keys = None
        assert self.empty_obdict.from_keys is None


if __name__ == '__main__':
    unittest.main()