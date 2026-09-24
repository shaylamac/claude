#!/usr/bin/env python3
"""Canon consistency checker.

Scans manuscript chapters (.md / .txt) against a structured canon file (YAML)
and reports hard-fact contradictions: misspelled names, banned terms, physical
trait conflicts, wrong titles, wrong ages, wrong family relations, dead
characters appearing, and characters appearing before they are introduced.

Nuance (voice, relationship state, who-knows-what, world-rule logic) is left to
the companion Claude skill, which reads this script's report.

Usage:
    python canon_check.py check  --canon canon.yaml chapters/ [--when ID] [--format md|json] [--out FILE]
    python canon_check.py validate --canon canon.yaml
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

DEFAULT_TRAIT_VOCAB = {
    "eyes": {
        "keywords": ["eyes", "eye", "eyed"],
        "values": ["amber", "black", "blue", "brown", "copper", "gold", "golden", "gray",
                   "grey", "green", "hazel", "silver", "violet", "red", "emerald", "sapphire"],
    },
    "hair": {
        "keywords": ["hair", "haired", "curls", "braid", "braids", "locks"],
        "values": ["auburn", "black", "blond", "blonde", "brown", "chestnut", "copper",
                   "golden", "gold", "gray", "grey", "red", "silver", "white", "raven", "dark"],
    },
}
# Spelling variants treated as the same value.
VALUE_ALIASES = {"grey": "gray", "blonde": "blond", "golden": "gold", "raven": "black"}
COPULAS = {"was", "were", "is", "are", "turned", "gone", "went", "burned", "glowed", "flashed"}

DEFAULT_TITLES = ["King", "Queen", "Prince", "Princess", "Lord", "Lady", "Duke", "Duchess",
                  "Sir", "Dame", "Emperor", "Empress", "Regent", "Commander", "Captain",
                  "General", "Alpha", "Luna", "Priestess", "Priest"]
RELATIONS = ["mother", "father", "brother", "sister", "son", "daughter", "husband", "wife",
             "uncle", "aunt", "cousin", "niece", "nephew", "grandmother", "grandfather",
             "twin", "betrothed", "mate", "stepmother", "stepfather", "half-brother",
             "half-sister", "guardian", "ward"]
NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
NUMBER_WORDS.update({"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
                     "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100})

SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])[\"'”’)]*\s+")
WORD = re.compile(r"[A-Za-z]+")
CAP_WORD = re.compile(r"\b[A-Z][a-zA-Z’'-]*[a-zA-Z]\b")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    file: str
    line: int
    severity: str  # error | warning | info
    check: str
    message: str
    snippet: str = ""


class Canon:
    def __init__(self, data: dict):
        self.raw = data or {}
        self.series = self.raw.get("series", "Untitled series")
        self.timeline = [t for t in self.raw.get("timeline") or [] if t and t.get("id")]
        self.timeline_index = {t["id"]: i for i, t in enumerate(self.timeline)}
        self.characters = [c for c in self.raw.get("characters") or [] if c and c.get("name")]
        terms = self.raw.get("terms") or {}
        self.canonical_terms = [t for t in terms.get("canonical") or [] if t]
        self.banned_terms = terms.get("banned") or {}
        self.ignore_words = set(terms.get("ignore") or [])
        self.places = [p["name"] if isinstance(p, dict) else p
                       for p in self.raw.get("places") or [] if p]

        vocab = {k: {"keywords": list(v["keywords"]), "values": list(v["values"])}
                 for k, v in DEFAULT_TRAIT_VOCAB.items()}
        for trait, extra in (self.raw.get("trait_vocab") or {}).items():
            entry = vocab.setdefault(trait, {"keywords": [trait], "values": []})
            entry["keywords"] += extra.get("keywords") or []
            entry["values"] += extra.get("values") or []
        self.trait_vocab = vocab

        titles = set(DEFAULT_TITLES)
        for c in self.characters:
            titles.update(str(t) for t in (c.get("titles") or {}).values())
        self.titles = sorted(titles, key=len, reverse=True)

        self.alias_map = self._build_alias_map()

    @classmethod
    def load(cls, path: Path) -> "Canon":
        with open(path, encoding="utf-8") as fh:
            return cls(yaml.safe_load(fh))

    def _build_alias_map(self) -> dict[str, dict]:
        """Map every way a character can be named -> character entry."""
        alias_map: dict[str, dict] = {}
        first_names: dict[str, list[dict]] = {}
        for c in self.characters:
            alias_map[c["name"]] = c
            for a in c.get("aliases") or []:
                alias_map[str(a)] = c
            first = c["name"].split()[0]
            first_names.setdefault(first, []).append(c)
        # A bare first name counts as an alias only when it is unambiguous.
        for first, owners in first_names.items():
            if len(owners) == 1 and first not in alias_map:
                alias_map[first] = owners[0]
        return alias_map

    def lexicon(self) -> set[str]:
        words: set[str] = set(self.ignore_words)
        for phrase in [*self.alias_map, *self.canonical_terms, *self.places, *self.titles]:
            words.update(str(phrase).split())
        for t in self.timeline:
            words.update(str(t.get("label", "")).split())
        return {w.strip(".,;:!?\"'") for w in words if w}

    def point(self, when: str | None) -> int | None:
        return self.timeline_index.get(when) if when else None

    def effective(self, mapping: dict | None, when_idx: int | None):
        """Value from a {timeline_id: value} map in effect at when_idx."""
        if not mapping:
            return None
        if when_idx is None:
            values = set(map(str, mapping.values()))
            return next(iter(values)) if len(values) == 1 else None
        best, best_idx = None, -1
        for tid, value in mapping.items():
            idx = self.timeline_index.get(tid)
            if idx is not None and best_idx < idx <= when_idx:
                best, best_idx = value, idx
        return best


# ---------------------------------------------------------------------------
# Manuscript parsing
# ---------------------------------------------------------------------------

@dataclass
class Sentence:
    text: str
    line: int
    para: int = 0


def parse_manuscript(text: str) -> tuple[dict, list[Sentence]]:
    """Split front matter from body and return sentences with line numbers."""
    meta: dict = {}
    body_start = 0
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                meta = yaml.safe_load("\n".join(lines[1:i])) or {}
                body_start = i + 1
                break

    sentences: list[Sentence] = []
    para: list[str] = []
    para_line = body_start + 1
    para_no = 0

    def flush():
        nonlocal para_no
        if not para:
            return
        para_no += 1
        joined = "\n".join(para)
        offset = 0
        for chunk in SENTENCE_SPLIT.split(joined):
            pos = joined.find(chunk, offset)
            if chunk.strip():
                sentences.append(Sentence(" ".join(chunk.split()),
                                          para_line + joined.count("\n", 0, max(pos, 0)), para_no))
            offset = max(pos, 0) + len(chunk)

    for n, line in enumerate(lines[body_start:], start=body_start + 1):
        if line.strip():
            if not para:
                para_line = n
            para.append(line)
        else:
            flush()
            para = []
    flush()
    return meta, sentences


def parse_number(token: str) -> int | None:
    token = token.lower()
    if token.isdigit():
        return int(token)
    total = 0
    for part in token.split("-"):
        if part not in NUMBER_WORDS:
            return None
        total += NUMBER_WORDS[part]
    return total


def norm_value(v: str) -> str:
    v = v.lower()
    return VALUE_ALIASES.get(v, v)


def mentions(sentence: str, canon: Canon) -> list[tuple[int, int, str]]:
    """(start, end, character name) for every alias occurrence, in text order."""
    found = []
    for alias, char in canon.alias_map.items():
        for m in re.finditer(rf"\b{re.escape(alias)}\b", sentence):
            found.append((m.start(), m.end(), char["name"]))
    # Drop mentions nested inside a longer one ("Maren" inside "Maren Vale").
    found.sort(key=lambda x: (x[0], -x[1]))
    kept: list[tuple[int, int, str]] = []
    for m in found:
        if not kept or m[0] >= kept[-1][1]:
            kept.append(m)
    return kept


def names_in(sentence: str, canon: Canon) -> dict[str, list[str]]:
    """Character name -> aliases used for them in this sentence."""
    found: dict[str, list[str]] = {}
    for start, end, name in mentions(sentence, canon):
        found.setdefault(name, []).append(sentence[start:end])
    return found


@dataclass
class Context:
    """Who a sentence is about, for trait/age attribution."""
    mentions: list[tuple[int, int, str]]
    carried: str | None  # sole character of the previous sentence in this paragraph

    def subject_at(self, pos: int) -> tuple[str, bool] | None:
        """Character a description at `pos` most likely refers to, and whether it was inferred."""
        before = [m for m in self.mentions if m[1] <= pos]
        if before:
            return before[-1][2], False
        names = {m[2] for m in self.mentions}
        if len(names) == 1:
            return next(iter(names)), False
        if not names and self.carried:
            return self.carried, True
        return None


def short(text: str, limit: int = 160) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_banned(canon: Canon, s: Sentence, f: str) -> list[Finding]:
    out = []
    for wrong, right in canon.banned_terms.items():
        for m in re.finditer(rf"\b{re.escape(str(wrong))}\b", s.text, re.IGNORECASE):
            out.append(Finding(f, s.line, "error", "banned-term",
                               f'"{m.group(0)}" is not canon; use "{right}".', short(s.text)))
    for term in canon.canonical_terms:
        if " " not in term:
            continue  # single words are handled by the spelling check
        for m in re.finditer(rf"\b{re.escape(term)}\b", s.text, re.IGNORECASE):
            if m.group(0) != term:
                out.append(Finding(f, s.line, "warning", "term-case",
                                   f'"{m.group(0)}" should be written "{term}".', short(s.text)))
    return out


def check_traits(canon: Canon, s: Sentence, f: str, ctx: Context) -> list[Finding]:
    tokens = [(m.group(0).lower(), m.start()) for m in WORD.finditer(s.text)]
    words = [t for t, _ in tokens]
    out = []
    for trait, vocab in canon.trait_vocab.items():
        values = {norm_value(v) for v in vocab["values"]}
        keywords = {k.lower() for k in vocab["keywords"]}
        for k, tok in enumerate(words):
            if tok not in keywords:
                continue
            idx = list(range(max(0, k - 3), k))
            if k + 1 < len(words) and words[k + 1] in COPULAS:
                idx += list(range(k + 2, min(k + 4, len(words))))
            for i in idx:
                w = words[i]
                if norm_value(w) not in values:
                    continue
                subject = ctx.subject_at(tokens[i][1])
                if not subject:
                    continue
                name, inferred = subject
                traits = canon.alias_map[name].get("traits") or {}
                if trait not in traits:
                    continue
                canon_vals = {norm_value(v) for v in WORD.findall(str(traits[trait]))}
                if norm_value(w) in canon_vals:
                    continue
                note = " (subject inferred from previous sentence)" if inferred else ""
                out.append(Finding(
                    f, s.line, "warning" if inferred else "error", "trait",
                    f'{name}\'s {trait}: canon says "{traits[trait]}", text says "{w}"{note}.',
                    short(s.text)))
    return out


def check_titles(canon: Canon, s: Sentence, f: str, when_idx: int | None) -> list[Finding]:
    out = []
    title_alt = "|".join(re.escape(t) for t in canon.titles)
    for alias, char in canon.alias_map.items():
        expected = canon.effective(char.get("titles"), when_idx)
        if not expected:
            continue
        for m in re.finditer(rf"\b({title_alt})\s+{re.escape(alias)}\b", s.text):
            if m.group(1).lower() != str(expected).lower():
                out.append(Finding(f, s.line, "error", "title",
                                   f'{char["name"]} is "{expected}" at this point, text says "{m.group(1)}".',
                                   short(s.text)))
    return out


def expected_age(canon: Canon, char: dict, when_idx: int | None) -> tuple[int, int] | None:
    """Return (age, tolerance) or None if canon can't say."""
    if when_idx is None:
        return None
    point = canon.timeline[when_idx]
    if "born" in char and "year" in point:
        return int(point["year"]) - int(char["born"]), 1
    ages = char.get("ages") or {}
    if point["id"] in ages:
        return int(ages[point["id"]]), 0
    return None


AGE_PATTERNS = [
    re.compile(r"\b([\w-]+)[- ]years?[- ]old\b", re.I),
    re.compile(r"\bage of ([\w-]+)\b", re.I),
    re.compile(r"\bturned ([\w-]+)\b", re.I),
]


def check_ages(canon: Canon, s: Sentence, f: str, ctx: Context, when_idx: int | None) -> list[Finding]:
    out = []
    for pat in AGE_PATTERNS:
        for m in pat.finditer(s.text):
            n = parse_number(m.group(1))
            subject = ctx.subject_at(m.start())
            if n is None or not subject:
                continue
            name, inferred = subject
            exp = expected_age(canon, canon.alias_map[name], when_idx)
            if exp and abs(n - exp[0]) > exp[1]:
                note = " (subject inferred from previous sentence)" if inferred else ""
                out.append(Finding(f, s.line, "warning", "age",
                                   f"{name} should be about {exp[0]} here, text says {n}{note}.",
                                   short(s.text)))
    return out


def check_relations(canon: Canon, s: Sentence, f: str) -> list[Finding]:
    if not canon.alias_map:
        return []
    out = []
    names = sorted(canon.alias_map, key=len, reverse=True)
    name_alt = "|".join(re.escape(n) for n in names)
    rel_alt = "|".join(re.escape(r) for r in sorted(RELATIONS, key=len, reverse=True))
    patterns = [
        re.compile(rf"\b(?P<a>{name_alt})['’]s (?P<rel>{rel_alt}),? (?P<b>{name_alt})\b"),
        re.compile(rf"\b(?P<b>{name_alt}), (?P<a>{name_alt})['’]s (?P<rel>{rel_alt})\b"),
    ]
    for pat in patterns:
        for m in pat.finditer(s.text):
            a = canon.alias_map[m.group("a")]
            b = canon.alias_map[m.group("b")]
            rel = m.group("rel")
            recorded = (a.get("relations") or {}).get(rel)
            if recorded is None:
                out.append(Finding(f, s.line, "info", "relation",
                                   f'Text says {b["name"]} is {a["name"]}\'s {rel}; canon has no "{rel}" '
                                   f"for {a['name']}. Add it if this is new canon.", short(s.text)))
                continue
            allowed = recorded if isinstance(recorded, list) else [recorded]
            if b["name"] not in allowed:
                out.append(Finding(f, s.line, "error", "relation",
                                   f"{a['name']}'s {rel} is {', '.join(map(str, allowed))} in canon, "
                                   f"text says {b['name']}.", short(s.text)))
    return out


def check_spelling(canon: Canon, sentences: list[Sentence], f: str) -> list[Finding]:
    lexicon = canon.lexicon()
    lex_lower = {w.lower() for w in lexicon}
    candidates = [w for w in lexicon if len(w) >= 4 and w not in canon.titles]
    seen: dict[str, list[int]] = {}
    for s in sentences:
        for tok in CAP_WORD.findall(s.text):
            tok = re.sub(r"['’]s$", "", tok)
            if len(tok) < 4 or tok in lexicon or tok in canon.ignore_words:
                continue
            if tok.lower() in lex_lower:
                continue
            seen.setdefault(tok, []).append(s.line)
    out = []
    for tok, lines in seen.items():
        match = difflib.get_close_matches(tok, candidates, n=1, cutoff=0.8)
        if match:
            where = f" (also lines {', '.join(map(str, lines[1:6]))})" if len(lines) > 1 else ""
            out.append(Finding(f, lines[0], "warning", "spelling",
                               f'"{tok}" looks like a misspelling of "{match[0]}"{where}.'))
    return out


def check_presence(canon: Canon, sentences: list[Sentence], f: str, when_idx: int | None) -> list[Finding]:
    if when_idx is None:
        return []
    first_seen: dict[str, tuple[int, int]] = {}
    for s in sentences:
        for name in names_in(s.text, canon):
            line, count = first_seen.get(name, (s.line, 0))
            first_seen[name] = (line, count + 1)
    out = []
    when_label = canon.timeline[when_idx]["id"]
    for name, (line, count) in first_seen.items():
        char = canon.alias_map[name]
        died = canon.point(char.get("died_at"))
        intro = canon.point(char.get("first_appears"))
        if died is not None and when_idx > died:
            out.append(Finding(f, line, "warning", "dead-character",
                               f"{name} died at \"{char['died_at']}\" but is named {count}x in a chapter set at "
                               f"\"{when_label}\". Fine if memory/flashback; otherwise a continuity error."))
        if intro is not None and when_idx < intro:
            out.append(Finding(f, line, "warning", "early-appearance",
                               f"{name} first appears at \"{char['first_appears']}\" but is named {count}x in a "
                               f"chapter set earlier (\"{when_label}\")."))
    return out


def check_file(canon: Canon, path: Path, when_override: str | None = None) -> tuple[dict, list[Finding]]:
    text = path.read_text(encoding="utf-8")
    meta, sentences = parse_manuscript(text)
    when = when_override or meta.get("when")
    f = str(path)
    findings: list[Finding] = []
    when_idx = canon.point(when)
    if when and when_idx is None:
        findings.append(Finding(f, 1, "error", "timeline",
                                f'Front matter "when: {when}" is not a timeline id in the canon file.'))
    elif not when:
        findings.append(Finding(f, 1, "info", "timeline",
                                'No "when:" front matter; timeline, age and title-by-era checks were skipped.'))

    prev_para, carried = None, None
    for s in sentences:
        found = mentions(s.text, canon)
        if s.para != prev_para:
            prev_para, carried = s.para, None
        ctx = Context(found, carried)
        findings += check_banned(canon, s, f)
        findings += check_traits(canon, s, f, ctx)
        findings += check_titles(canon, s, f, when_idx)
        findings += check_ages(canon, s, f, ctx, when_idx)
        findings += check_relations(canon, s, f)
        names = {m[2] for m in found}
        if len(names) == 1:
            carried = next(iter(names))
        elif names:
            carried = None
    findings += check_spelling(canon, sentences, f)
    findings += check_presence(canon, sentences, f, when_idx)
    order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda x: (x.line, order[x.severity]))
    return {"file": f, "when": when}, findings


# ---------------------------------------------------------------------------
# Canon validation
# ---------------------------------------------------------------------------

def validate_canon(canon: Canon) -> list[Finding]:
    out: list[Finding] = []
    src = "canon"
    ids = [t["id"] for t in canon.timeline]
    for dup in {i for i in ids if ids.count(i) > 1}:
        out.append(Finding(src, 0, "error", "timeline", f'Duplicate timeline id "{dup}".'))
    known = {c["name"] for c in canon.characters}
    aliases: dict[str, str] = {}
    for c in canon.characters:
        name = c["name"]
        for field_name in ("died_at", "first_appears"):
            v = c.get(field_name)
            if v and v not in canon.timeline_index:
                out.append(Finding(src, 0, "error", "reference", f'{name}.{field_name} "{v}" is not a timeline id.'))
        for field_name in ("ages", "titles"):
            for tid in (c.get(field_name) or {}):
                if tid not in canon.timeline_index:
                    out.append(Finding(src, 0, "error", "reference",
                                       f'{name}.{field_name} key "{tid}" is not a timeline id.'))
        for rel, targets in (c.get("relations") or {}).items():
            for t in targets if isinstance(targets, list) else [targets]:
                if t not in known:
                    out.append(Finding(src, 0, "warning", "reference",
                                       f'{name}.relations.{rel} "{t}" is not a listed character.'))
        for a in c.get("aliases") or []:
            if a in aliases and aliases[a] != name:
                out.append(Finding(src, 0, "warning", "alias",
                                   f'Alias "{a}" is shared by {aliases[a]} and {name}; it will be ambiguous.'))
            aliases[a] = name
        if c.get("status") == "dead" and not c.get("died_at"):
            out.append(Finding(src, 0, "info", "completeness", f"{name} is dead but has no died_at."))
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

ICON = {"error": "🔴 ERROR", "warning": "🟡 WARNING", "info": "🔵 INFO"}


def render_markdown(canon: Canon, results: list[tuple[dict, list[Finding]]]) -> str:
    all_f = [x for _, fs in results for x in fs]
    counts = {s: sum(1 for x in all_f if x.severity == s) for s in ICON}
    lines = [
        f"# Canon Check Report: {canon.series}",
        "",
        f"**Files:** {len(results)} · **Errors:** {counts['error']} · "
        f"**Warnings:** {counts['warning']} · **Info:** {counts['info']}",
        "",
    ]
    for meta, findings in results:
        when = f" (when: `{meta['when']}`)" if meta.get("when") else ""
        lines += [f"## {meta['file']}{when}", ""]
        if not findings:
            lines += ["✅ No hard-fact conflicts found.", ""]
            continue
        for x in findings:
            loc = f"L{x.line}" if x.line else "canon"
            lines.append(f"- **{ICON[x.severity]}** `{loc}` · *{x.check}*: {x.message}")
            if x.snippet:
                lines.append(f"  > {x.snippet}")
        lines.append("")
    lines += [
        "---",
        "_Script checks cover hard facts only. Voice, relationship state, who-knows-what and "
        "world-rule logic still need the skill's review pass._",
    ]
    return "\n".join(lines) + "\n"


def collect_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(x for x in p.rglob("*") if x.suffix.lower() in {".md", ".txt"})
        elif p.exists():
            files.append(p)
        else:
            raise SystemExit(f"Not found: {p}")
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check manuscripts against a canon file.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="Check chapters against canon")
    c.add_argument("paths", nargs="+", help="Chapter files or directories (.md/.txt)")
    c.add_argument("--canon", required=True, type=Path)
    c.add_argument("--when", help="Timeline id to assume (overrides front matter)")
    c.add_argument("--format", choices=["md", "json"], default="md")
    c.add_argument("--out", type=Path, help="Write report to this file instead of stdout")
    c.add_argument("--fail-on", choices=["error", "warning", "never"], default="error")

    v = sub.add_parser("validate", help="Lint the canon file itself")
    v.add_argument("--canon", required=True, type=Path)

    args = ap.parse_args(argv)
    canon = Canon.load(args.canon)

    if args.cmd == "validate":
        findings = validate_canon(canon)
        for x in findings:
            print(f"{ICON[x.severity]}: {x.message}")
        if not findings:
            print(f"✅ Canon file OK: {len(canon.characters)} characters, {len(canon.timeline)} timeline points.")
        return 1 if any(x.severity == "error" for x in findings) else 0

    results = [check_file(canon, p, args.when) for p in collect_files(args.paths)]
    if args.format == "json":
        report = json.dumps([{**meta, "findings": [asdict(x) for x in fs]} for meta, fs in results], indent=2)
    else:
        report = render_markdown(canon, results)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Report written to {args.out}")
    else:
        sys.stdout.write(report)

    severities = {x.severity for _, fs in results for x in fs}
    if args.fail_on == "error":
        return 1 if "error" in severities else 0
    if args.fail_on == "warning":
        return 1 if severities & {"error", "warning"} else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
