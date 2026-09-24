# Canon Consistency Checker

Catches continuity errors in fiction manuscripts by checking chapters against a
structured canon file. Built first for **Marked By Fate** (Spiral Kingdom).

It works in two layers:

| Layer | What | Catches |
|---|---|---|
| **Script** `canon_checker/canon_check.py` | Fast, repeatable, rule-based | Misspelled names/places, banned or retconned terms, wrong eye/hair colour, wrong title for the era, wrong age, wrong family relation, dead characters appearing, characters appearing before their introduction |
| **Skill** `.claude/skills/mbf-canon-check/` | Claude review pass on top of the script | Voice drift, relationship state, who-knows-what (secrets and reveals), world-rule/magic violations, paraphrased facts the regex misses |

## Quick start

```bash
pip install -r requirements.txt

# 1. Fill in canon/marked-by-fate/canon.yaml, then lint it
python canon_checker/canon_check.py validate --canon canon/marked-by-fate/canon.yaml

# 2. Check chapters (files or whole folders)
python canon_checker/canon_check.py check --canon canon/marked-by-fate/canon.yaml \
  canon/marked-by-fate/chapters/ --out reports/canon-report.md
```

Try it on the made-up sample series:

```bash
python canon_checker/canon_check.py check --canon examples/sample-canon.yaml examples/chapters
```

## Chapter setup

Put a `when:` line at the top of each chapter so era-dependent checks (titles, ages,
deaths, introductions) know where it sits on the timeline:

```markdown
---
when: coronation
---
Queen Maren stood on the walls...
```

Without it, those checks are skipped (reported as info). `--when <id>` overrides it.

## Options

| Flag | Meaning |
|---|---|
| `--format md\|json` | Markdown report (default) or JSON for tooling |
| `--out FILE` | Write the report to a file |
| `--fail-on error\|warning\|never` | Exit code policy (default: exit 1 on any error) |

## Severity

- 🔴 **error**: contradicts an explicit canon fact.
- 🟡 **warning**: probable problem needing judgement (flashbacks, inferred subjects, ages ±1).
- 🔵 **info**: the text states something canon doesn't cover yet. Decide and record it.

## Canon file

See the comments in `canon/marked-by-fate/canon.yaml` and the filled-in
`examples/sample-canon.yaml`. Sections: `timeline`, `characters` (aliases, born/ages,
status, died_at, first_appears, traits, titles by era, relations, voice, arc), `places`,
`terms` (canonical / banned / ignore), `trait_vocab` (teach it new traits such as fate
marks), `world_rules`, `knowledge`.

## Tests

```bash
python -m unittest discover tests
```

## Known limits (by design)

- Pronoun attribution only carries within a paragraph and only when one character is
  named. Anything ambiguous is skipped, not guessed; the skill pass picks it up.
- Trait checks look at colour words within three words of the trait noun
  ("her storm-grey eyes", "eyes were blue"). Similes and metaphor are left to the skill.
