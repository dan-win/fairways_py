import unittest
# import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class TentativeTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from fairways.decorators import tentative
        from fairways.ci import helpers
        cls.tentative = tentative
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_tentative(self):
        tentative = self.tentative
        @tentative.tentative("to-do:...")
        def temporary():
            "Some draft func"
            pass

        self.assertEqual(temporary.__doc__, "* tentative *:\nto-do:...\nSome draft func")        