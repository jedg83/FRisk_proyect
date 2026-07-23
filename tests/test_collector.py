import unittest

from src import collector


class CollectorFallbackTests(unittest.TestCase):
    def test_extract_entities_falls_back_to_regex(self):
        people, orgs, locations = collector.extract_entities(
            "Police arrested John Doe in Lagos, Nigeria, for bribery at Shell plc."
        )

        self.assertIn("John Doe", people)
        self.assertTrue(any("Shell" in org for org in orgs))
        self.assertIn("Nigeria", locations)


if __name__ == "__main__":
    unittest.main()
