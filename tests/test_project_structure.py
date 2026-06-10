from pathlib import Path
import unittest
import yaml


class ProjectStructureTests(unittest.TestCase):
    def test_shared_scenario_files_exist(self):
        self.assertTrue(Path("scenario/ai_builder_scenario.md").is_file())
        self.assertTrue(Path("scenario/reviewer_considerations.yaml").is_file())

    def test_reviewer_considerations_are_not_secret_scoring_criteria(self):
        data = yaml.safe_load(Path("scenario/reviewer_considerations.yaml").read_text())

        self.assertIs(data["not_secret_scoring_criteria"], True)
        self.assertIsInstance(data["considerations"], list)
        self.assertGreater(len(data["considerations"]), 0)


if __name__ == "__main__":
    unittest.main()
