import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class FromTypeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # from fairways.api import core, triggers
        from fairways.decorators import fromtype
        cls.fromtype = fromtype

    def test_fromtype(self):
        fromtype = self.fromtype


        class CustomClass:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class MyClass(fromtype.FromTypeMixin):

            def __init__(self, value=None):
                self.value = value

            @fromtype.implement(int)
            def _from_int(self, value):
                self.value = f"From int: {value}"

            @fromtype.implement(str)
            def _from_str(self, value):
                self.value = f"From str: {value}"

            @fromtype.implement(dict)
            def _from_dict(self, value):
                self.value = f"From dict: {value}"

            @fromtype.implement(CustomClass)
            def _from_obj(self, value):
                self.value = f"From CustomClass: {value}"
            
            def __str__(self):
                return self.value

        self.assertEqual('From int: 1', MyClass.fromtype(1).value)
        self.assertEqual('From str: Text', MyClass.fromtype("Text").value)
        self.assertEqual("From dict: {'a': 1}", MyClass.fromtype(dict(a=1)).value)
        self.assertEqual('From CustomClass: CustomClass:objectName', MyClass.fromtype(CustomClass("objectName")).value)
