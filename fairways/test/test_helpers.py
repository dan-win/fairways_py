import unittest


def setUpModule():
    pass

def tearDownModule():
    pass

class TestRecSysEvent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api import helpers
        cls.helpers = helpers

    @classmethod
    def tearDownClass(cls):
        pass

    def test_nested(self):
        """
        """
        get_nested = self.helpers.get_nested
        deep_dict = {"1":{"2":{"3":"nested item"}}}
        result = get_nested(deep_dict, "1/2/3")
        self.assertEqual(result, 'nested item')
    
    def test_parent(self):
        """
        """
        get_parent = self.helpers.get_parent
        deep_dict = {"1":{"2":{"3":"nested item"}}}
        result = get_parent(deep_dict, "1/2/3")
        self.assertEqual(result, {'3': 'nested item'}, "Should return a most inner dict")
        result = get_parent(deep_dict, "1")
        self.assertEqual(result, deep_dict, "Should return the topmost itself")

if __name__ == '__main__':
    unittest.main(verbosity=2)
