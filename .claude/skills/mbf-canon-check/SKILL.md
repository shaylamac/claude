---
name: mbf-canon-check
description: Check a Marked By Fate (Spiral Kingdom) chapter, scene or draft for canon consistency. Use when Shayla says "check this against canon", "canon check", "does this contradict anything", "continuity check", or pastes/uploads a chapter for Marked By Fate. Runs the hard-fact script first, then reviews voice, relationship state, who-knows-what and world rules.
---

# Marked By Fate: Canon Consistency Check

Two passes. The script catches literal facts reliably. You catch everything that needs
judgement. Never invent canon: if something isn't in the canon file, it's a
**question**, not an error.

## Files

- Canon source of truth: `canon/marked-by-fate/canon.yaml`
- Chapters: `canon/marked-by-fate/chapters/` (Markdown or .txt, with `when:` front matter)
- Script: `canon_checker/canon_check.py`
- Reports: `reports/`

## Step 0: Get the text in place

If the chapter was pasted in chat, save it to `canon/marked-by-fate/chapters/<slug>.md`.
Ask which timeline point it's set at if it's not obvious, and add front matter:

```markdown
---
when: <timeline id from canon.yaml>
---
```

If `canon.yaml` has no characters yet, stop and offer to fill it from the Character
Bible / family trees Shayla pastes in first.

## Step 1: Script pass (hard facts)

```bash
python canon_checker/canon_check.py validate --canon canon/marked-by-fate/canon.yaml
python canon_checker/canon_check.py check --canon canon/marked-by-fate/canon.yaml \
  canon/marked-by-fate/chapters/<file>.md --out reports/<file>-canon.md
```

Read the report. For each finding:
- 🔴 **error**: confirm it's real (read the sentence in context), then keep it.
- 🟡 **warning**: judge it. Dead characters may be in a flashback or memory. Inferred
  subjects ("His blue eyes…") may point at the wrong person. Drop false positives
  and say why in one line.
- 🔵 **info**: things the canon file doesn't cover. Turn them into questions.

## Step 2: Review pass (judgement)

Read the whole chapter alongside `canon.yaml`, and check:

1. **Character facts the regex missed**: traits described without a name nearby,
   paraphrased relations ("the girl's father"), titles used in dialogue.
2. **Timeline & events**: events referenced out of order, time elapsed between
   scenes, seasons, injuries that heal too fast, anyone present who shouldn't be.
3. **Knowledge**: using `knowledge`, does any character act on, hint at or say
   something before its `revealed` point for them?
4. **World rules**: does any scene break a rule in `world_rules` (magic limits, fate
   marks, bonds, politics, geography/travel time)?
5. **Voice**: does dialogue match each character's `voice` notes? Flag lines that
   sound like a different character, or like modern slang if that's off-tone.
6. **Relationships**: does each relationship's temperature match the `arc` notes
   for this timeline point (trust, hostility, romance milestones)?

## Step 3: Report

Append a `## Review pass` section to the report file in this format:

```markdown
## Review pass

### 🔴 Must fix
- **L42 · Knowledge**: Kael references the prophecy's second verse, which he doesn't learn until `<id>`.
  > "quoted line"
  **Fix:** suggested rewrite or option.

### 🟡 Check
- ...

### ❓ Canon questions (not in canon.yaml yet)
- Is X's eye color established anywhere? Text says grey.

### ✅ Confirmed consistent
- One line summary of what was checked and held up.
```

Then give Shayla a short chat summary: counts, the top 3 issues, and the report path.

## Step 4: Close the loop

If Shayla confirms new canon while resolving questions, update `canon.yaml` (and
use the `mbf-canon-sync` skill if the decision also needs to propagate to the
Character Bible, family trees or ChatGPT bundle). Re-run `validate` after edits.

## Rules

- Canon file wins over memory. Cite the canon field when calling something an error.
- Never rewrite the chapter unless asked; suggest fixes inline.
- Don't nitpick prose style; this is a continuity check, not a line edit.
