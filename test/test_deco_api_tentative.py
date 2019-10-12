import unittest
# import unittest.mock

def setUpModule():
    pass

def tearDownModule():
    pass

class ApiTagTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from fairways.decorators import apitag
        from fairways.ci import helpers
        cls.apitag = apitag
        root = helpers.getLogger()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_tentative(self):
        apitag = self.apitag
        @apitag.tentative("to-do:...")
        def temporary():
            "Some draft func"
            pass

        self.assertEqual(temporary.__doc__, "* tentative *:\nto-do:...\nSome draft func")        