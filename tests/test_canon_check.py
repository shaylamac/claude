"""Tests for the canon checker, run with: python -m unittest discover tests"""
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "canon_checker"))

import canon_check as cc  # noqa: E402

CANON = cc.Canon.load(ROOT / "examples" / "sample-canon.yaml")


def run(body: str, when: str | None = "coronation"):
    front = f"---\nwhen: {when}\n---\n" if when else ""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(front + textwrap.dedent(body))
    _, findings = cc.check_file(CANON, Path(fh.name))
    return findings


def checks(findings, severity=None):
    return [f.check for f in findings if severity is None or f.severity == severity]


class TraitTests(unittest.TestCase):
    def test_conflicting_eye_color_is_error(self):
        self.assertIn("trait", checks(run("Maren Vale looked up, her blue eyes cold."), "error"))

    def test_canon_color_passes(self):
        self.assertNotIn("trait", checks(run("Maren's golden eyes narrowed. Mare had green eyes.")))

    def test_spelling_variant_passes(self):
        self.assertNotIn("trait", checks(run("Corin's grey eyes softened.")))

    def test_pronoun_subject_is_inferred_as_warning(self):
        f = run("Corin laughed. His blue eyes were bright.")
        self.assertIn("trait", checks(f, "warning"))

    def test_subject_does_not_carry_across_paragraphs(self):
        self.assertNotIn("trait", checks(run("Corin laughed.\n\nHis blue eyes were bright.")))

    def test_nearest_name_wins(self):
        # Blue eyes belong to Corin (gray in canon), not Maren.
        f = run("Maren watched Corin, whose blue eyes were bright.")
        msgs = [x.message for x in f if x.check == "trait"]
        self.assertTrue(msgs and "Corin" in msgs[0])


class TermTests(unittest.TestCase):
    def test_banned_term(self):
        self.assertIn("banned-term", checks(run("They sailed the Glass Sea.")))

    def test_multiword_term_case(self):
        self.assertIn("term-case", checks(run("They reached saltspire keep.")))

    def test_misspelled_place(self):
        self.assertIn("spelling", checks(run("He rode from Harowmere.")))

    def test_ordinary_capitalised_words_are_not_flagged(self):
        self.assertNotIn("spelling", checks(run("Then Morning came. Every bell rang in Saltspire.")))


class TimelineTests(unittest.TestCase):
    def test_title_by_era(self):
        self.assertIn("title", checks(run("Lady Maren entered.", when="coronation")))
        self.assertNotIn("title", checks(run("Lady Maren entered.", when="prologue")))

    def test_dead_character_after_death(self):
        self.assertIn("dead-character", checks(run("Corin spoke.", when="aftermath")))
        self.assertNotIn("dead-character", checks(run("Corin spoke.", when="siege")))

    def test_early_appearance(self):
        self.assertIn("early-appearance", checks(run("Tavish Rook bowed.", when="prologue")))

    def test_age_from_birth_year(self):
        self.assertIn("age", checks(run("Maren was thirty years old.", when="coronation")))
        self.assertNotIn("age", checks(run("Maren was twenty years old.", when="coronation")))

    def test_missing_when_is_info(self):
        self.assertIn("timeline", checks(run("Maren waited.", when=None), "info"))

    def test_unknown_when_is_error(self):
        self.assertIn("timeline", checks(run("Maren waited.", when="nope"), "error"))


class RelationTests(unittest.TestCase):
    def test_wrong_relation(self):
        self.assertIn("relation", checks(run("Maren's mother, Tavish Rook, frowned."), "error"))

    def test_right_relation(self):
        self.assertNotIn("relation", checks(run("Maren's brother, Corin, frowned.")))

    def test_unrecorded_relation_is_info(self):
        self.assertIn("relation", checks(run("Maren's cousin, Tavish Rook, frowned.", when="siege"), "info"))


class ParsingTests(unittest.TestCase):
    def test_line_numbers_include_front_matter(self):
        f = run("Line one.\n\nThey sailed the Glass Sea.")
        banned = [x for x in f if x.check == "banned-term"][0]
        self.assertEqual(banned.line, 6)  # 3 front-matter lines + blank + text

    def test_validate_sample_canon_is_clean(self):
        self.assertEqual(cc.validate_canon(CANON), [])

    def test_validate_catches_bad_reference(self):
        bad = cc.Canon({"timeline": [{"id": "a"}],
                        "characters": [{"name": "X", "died_at": "b", "relations": {"mother": "Y"}}]})
        self.assertEqual(sorted(checks(cc.validate_canon(bad))), ["reference", "reference"])

    def test_empty_template_loads(self):
        canon = cc.Canon.load(ROOT / "canon" / "marked-by-fate" / "canon.yaml")
        self.assertEqual([f for f in cc.validate_canon(canon) if f.severity == "error"], [])


class EmptyCanonTests(unittest.TestCase):
    def test_checking_against_empty_template_does_not_crash(self):
        canon = cc.Canon.load(ROOT / "canon" / "marked-by-fate" / "canon.yaml")
        _, findings = cc.check_file(canon, ROOT / "examples" / "chapters" / "ch05-harrowmere.md")
        self.assertIn("timeline", checks(findings, "error"))  # "coronation" not in empty timeline


if __name__ == "__main__":
    unittest.main()
