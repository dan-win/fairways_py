import unittest

import fairways
from fairways.ci.utils import csv2py
from fairways.ci.templates import fixture_template

def setUpModule():
    pass

def tearDownModule():
    pass

class TestExamplePool(fixture_template.FixtureTestTemplate):
    subject_module = "examples.dummy_pool"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixture = {}

