import unittest
from spellchecker import SpellChecker


class TestSpellChecker(unittest.TestCase):
    def setUp(self):
        self.test_dict = "test_dict.txt"
        with open(self.test_dict, "w", encoding="utf-8") as f:
            f.write("кот\nкит\nмолоко\nрыба\nпесок\nспасибо\n")
        self.checker = SpellChecker(self.test_dict)

    def test_dictionary_load(self):
        self.assertIn("кот", self.checker.dictionary)
        self.assertIn("молоко", self.checker.dictionary)
        self.assertNotIn("собака", self.checker.dictionary)

    def test_damerau_levenshtein(self):
        self.assertEqual(self.checker.damerau_levenshtein("кот", "кот"), 0)
        self.assertEqual(self.checker.damerau_levenshtein("кот", "кит"), 1)
        self.assertEqual(self.checker.damerau_levenshtein("кот", "окт"), 1)
        self.assertEqual(self.checker.damerau_levenshtein("кот", "молоко"), float('inf'))

    def test_get_candidates(self):
        candidates = set(self.checker.get_candidates("спасиба"))
        self.assertIn("спасибо", candidates)

    def test_find_corrections(self):
        self.assertEqual(self.checker.find_corrections("кит"), [])
        self.assertIn("молоко", self.checker.find_corrections("молако"))

    def tearDown(self):
        import os
        os.remove(self.test_dict)


if __name__ == "__main__":
    unittest.main()
