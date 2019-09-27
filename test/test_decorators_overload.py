import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class OverloadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import asyncio
        from fairways.decorators import overload
        cls.overload = overload

    @classmethod
    def tearDownClass(cls):
        pass

    def test_overload_func(self):
        """
        """
        overload = self.overload

        @overload.overload(int)
        def func(data):
            return f"First case: {data}"

        @overload.overload(int, str)
        def func(data, text):
            return f"Second case: {data} + {text}"

        class MyClass:

            def __str__(self):
                return "Class"


        @overload.overload(int, str, MyClass)
        def func(data, text, obj):
            return f"Third case: {data} + {text} + {MyClass()}"

        self.assertEqual(func(1), "First case: 1")
        self.assertEqual(func(2, "test"), "Second case: 2 + test")
        self.assertEqual(func(3, "test", MyClass()), "Third case: 3 + test + Class")


    def test_overload_method(self):
        """
        """
        overload = self.overload

        class MyClass:

            @staticmethod
            @overload.overload(int)
            def func(data):
                return f"First case: {data}"

            @staticmethod
            @overload.overload(int, str)
            def func(data, text):
                return f"Second case: {data} + {text}"

            # @staticmethod
            # @overload.overload(int, str, "MyClass")
            # def func(data, text, obj):
            #     return f"Third case: {data} + {text} + {MyClass()}"

        obj = MyClass()

        self.assertEqual(obj.func(1), "First case: 1")
        self.assertEqual(obj.func(2, "test"), "Second case: 2 + test")
        # self.assertEqual(obj.func(3, "test", MyClass()), "Third case: 3 + test + Class")
