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
        from fairways.decorators import typecast
        cls.typecast = typecast

    def test_fromtype(self):
        typecast = self.typecast


        class CustomClass:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class CustomClass1:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class MyClass(typecast.FromTypeMixin):

            def __init__(self, value=None):
                self.value = value

            @typecast.fromtype(int)
            def _from_int(self, value):
                self.value = f"From int: {value}"

            @typecast.fromtype(str)
            def _from_str(self, value):
                self.value = f"From str: {value}"

            @typecast.fromtype(dict)
            def _from_dict(self, value):
                self.value = f"From dict: {value}"

            @typecast.fromtype(CustomClass)
            def _from_obj(self, value):
                self.value = f"From CustomClass: {value}"
            
            @typecast.fromtype('CustomClass1')
            def _from_obj(self, value):
                self.value = f"From CustomClass1: {value}"

            def __str__(self):
                return self.value

        self.assertEqual('From int: 1', MyClass.fromtype(1).value)
        self.assertEqual('From str: Text', MyClass.fromtype("Text").value)
        self.assertEqual("From dict: {'a': 1}", MyClass.fromtype(dict(a=1)).value)
        self.assertEqual('From CustomClass: CustomClass:objectName', MyClass.fromtype(CustomClass("objectName")).value)
        self.assertEqual('From CustomClass1: CustomClass1:objectName1', MyClass.fromtype(CustomClass1("objectName1")).value)

class IntoTypeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # from fairways.api import core, triggers
        from fairways.decorators import typecast
        cls.typecast = typecast

    def test_intotype(self):
        typecast = self.typecast


        class CustomClass:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class CustomClass1:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class MyClass(typecast.IntoTypeMixin):

            def __init__(self, value=None):
                self.value = value

            @typecast.intotype(int)
            def _into_int(self, value):
                return int(self.value)

            @typecast.intotype(str)
            def _into_str(self, value):
                return str(self.value)

            @typecast.intotype(dict)
            def _into_dict(self, value):
                return {"value": self.value}

            @typecast.intotype(CustomClass)
            def _into_obj(self, value):
                return CustomClass(self.value)
            
            @typecast.intotype('CustomClass1')
            def _into_obj(self, value):
                return CustomClass(self.value)

            def __str__(self):
                return self.value

        self.assertEqual(1, MyClass("1").intotype(int))
        self.assertEqual('1', MyClass("1").intotype(str))
        self.assertDictEqual({'value': '1'}, MyClass("1").intotype(dict))
        self.assertEqual('CustomClass:1', str(MyClass("1").intotype(CustomClass)))
        self.assertEqual('CustomClass:1', str(MyClass("1").intotype(CustomClass1)))
