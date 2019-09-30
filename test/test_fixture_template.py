import unittest
from fairways.ci.templates.fixture_template import FixtureTestTemplate

class FixtureTemplateTestCase(FixtureTestTemplate):
    subject_module = "fixture_subject"
    fixture = {
            "QUERY1": [{"name": "fixture_value"}]
        }

    def test_with_fixture(self):
        
        result = self.get_response_with_fixture()
        self.assertEqual(result, [{'name': 'fixture_value'}], "Should return 1 record with fields" )
