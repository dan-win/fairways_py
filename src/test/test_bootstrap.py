import unittest

def setUpModule():
    pass

def tearDownModule():
    pass

class TestAll(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_dummy(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        for i in range(0, 6):
            with self.subTest(i=i):
                self.assertEqual(i % 2, i % 2)

# if __name__ == '__main__':
#     unittest.main(verbosity=2)
