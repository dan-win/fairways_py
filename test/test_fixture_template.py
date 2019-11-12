import unittest
from fairways.ci.templates.fixture_template import FixtureTestTemplate

class FixtureTemplateTestCase(FixtureTestTemplate):
    subject_module = "test.fixture_subject"
    fixture = {
            "QUERY1": [{"name": "fixture_value"}]
        }

    def test_with_fixture(self):
        
        result = self.get_response_with_fixture()
        self.assertEqual(len(result), 1, "Should return 1 record with fields" )
        self.assertDictEqual(result[0], {'name': 'fixture_value'}, "Should return 1 record with expected fields" )
