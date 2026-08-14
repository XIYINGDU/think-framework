#!/usr/bin/env python3
"""Validate the local _williams research-guide artifacts."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, Tuple

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "the-craft-of-research"
BOOK = BOOK_DIR / "the-craft-of-research.md"
CONTENTS = BOOK_DIR / "005_contents.md"
CHAPTER_LEDGER = BOOK_DIR / "derived" / "chapter-principles.md"
HANDBOOK = BOOK_DIR / "derived" / "actionable-principles.md"
CLAUDE_AGENT = ROOT / ".claude" / "agents" / "williams.md"
CODEX_AGENT = ROOT / ".codex" / "agents" / "_williams.toml"
CODEX_SKILL = ROOT / ".codex" / "skills" / "williams-research-guide" / "SKILL.md"
CODEX_REFERENCE = (
    ROOT
    / ".codex"
    / "skills"
    / "williams-research-guide"
    / "references"
    / "actionable-principles.md"
)
CODEX_INTERFACE = (
    ROOT
    / ".codex"
    / "skills"
    / "williams-research-guide"
    / "agents"
    / "openai.yaml"
)
GROK_AGENT = ROOT / ".grok" / "agents" / "_williams.md"
GROK_HOME = Path.home() / ".grok" / "agents"
GROK_INSTALLED_AGENT = GROK_HOME / "_williams.md"
GROK_INSTALLED_HANDBOOK = GROK_HOME / "_williams-handbook.md"
GROK_INSTALLED_LEDGER = GROK_HOME / "_williams-chapter-principles.md"


class ValidationError(Exception):
    """Raised when a Williams artifact violates an expected invariant."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"missing file: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValidationError(f"empty file: {path.relative_to(ROOT)}")
    return text


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def normalized(text: str) -> str:
    return text.replace("­", "").replace(" ", " ")


def require_fragments(text: str, fragments: Tuple[str, ...], label: str) -> None:
    searchable = normalized(text)
    for fragment in fragments:
        check(
            normalized(fragment) in searchable,
            f"{label} is missing required text: {fragment!r}",
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_frontmatter(text: str, label: str) -> Dict[str, str]:
    check(text.startswith("---\n"), f"{label} has no YAML frontmatter")
    end = text.find("\n---\n", 4)
    check(end != -1, f"{label} has unterminated YAML frontmatter")

    fields: Dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def load_derived_artifacts() -> Tuple[str, str]:
    ledger = read_text(CHAPTER_LEDGER)
    handbook = read_text(HANDBOOK)
    return ledger, handbook


def validate_corpus() -> Tuple[str, str, str, str]:
    book = read_text(BOOK)
    contents = read_text(CONTENTS)
    ledger, handbook = load_derived_artifacts()

    check(len(book) > 500_000, "continuous book text is unexpectedly small")
    check(len(handbook.encode("utf-8")) > 40_000, "actionable handbook is unexpectedly small")

    require_fragments(
        book,
        (
            "Preface: The Aims of This Edition",
            "Introduction: Your Research and Your Audience",
            "1 From Topics to Questions",
            "9 Acknowledgments and Responses",
            "16 Research Presentations",
            "17 The Ethics of Research",
            "18 Advice for Teachers",
            "Our Debts",
            "Appendix: A Brief Guide to Bibliographic and Other Resources",
            "Index",
        ),
        "continuous book",
    )

    for chapter in range(1, 19):
        check(
            f"第 {chapter} 章" in ledger,
            f"chapter ledger is missing chapter {chapter}",
        )

    require_fragments(
        ledger,
        (
            "## 前言：The Aims of This Edition",
            "## 导论：Your Research and Your Audience",
            "## Our Debts、附录与索引",
            "## 覆盖矩阵",
            "## 来源边界",
        ),
        "chapter ledger",
    )

    contents_units = (
        "Pre­face: The Aims of This Edi­tion",
        "In­tro­duc­tion: Your Re­search and Your Audi­ence",
        "1 From Top­ics to Ques­tions",
        "18 Ad­vice for Teach­ers",
        "Our Debts",
        "Ap­pendix: A Brief Guide to Bib­li­o­graphic and Other Re­sources",
        "In­dex",
    )
    require_fragments(contents, contents_units, "table of contents")

    return book, contents, ledger, handbook


def validate_principles(handbook: str, ledger: str) -> None:
    ids = re.findall(r"(?m)^### AP-(\d{2,3})\b", handbook)
    expected = [f"{number:02d}" for number in range(1, 100)] + [
        str(number) for number in range(100, 131)
    ]
    check(len(ids) == 130, f"expected 130 AP headings, found {len(ids)}")
    check(ids == expected, "AP identifiers are duplicated, missing, or out of order")

    coverage_rows = re.findall(
        r"(?m)^\| (前言与导论|第 \d+ 章) \| AP-(\d+)–AP-(\d+) \|$", ledger
    )
    check(len(coverage_rows) == 19, "chapter coverage matrix must have 19 AP rows")

    next_start = 1
    for unit, start_text, end_text in coverage_rows:
        start = int(start_text)
        end = int(end_text)
        check(start == next_start, f"coverage gap before {unit}: expected AP-{next_start:02d}")
        check(end >= start, f"invalid AP range for {unit}: {start}–{end}")
        next_start = end + 1
    check(next_start == 131, "coverage matrix must end at AP-130")

    require_fragments(
        handbook,
        (
            "`我正在研究 X（聚焦主题），`",
            "Claim：`你要我相信什么？`",
            "Reasons：`为什么？`",
            "Evidence：`你怎么知道？`",
            "Warrant：`这个理由如何推出主张？`",
            "不得抄袭、冒领、歪曲来源、捏造或篡改证据",
            "时效性工具、机构政策或高风险事实时，应另行查找当前可靠来源",
            "内容仅以 Wayne C. Booth, Gregory G. Colomb, Joseph M. Williams",
        ),
        "actionable handbook",
    )
    require_fragments(
        ledger,
        (
            "本手册没有融合 *Beyond Feelings* 或其他研究框架",
            "需要当前事实、工具或机构政策时，另行核实",
        ),
        "chapter ledger source boundary",
    )


def validate_claude_agent(text: str) -> None:
    fields = parse_frontmatter(text, "Claude Williams agent")
    check(fields.get("name") == "williams", "Claude agent must register as 'williams'")
    check(
        re.fullmatch(r"[a-z][a-z0-9-]*", fields["name"]) is not None,
        "Claude agent name is not a supported identifier",
    )
    check("_williams" in fields.get("description", ""), "Claude description must route _williams")
    check("Read" in fields.get("tools", ""), "Claude agent must retain read access")

    require_fragments(
        text,
        (
            "You are **_williams**",
            "Claude Code registers you under the supported agent name `williams`",
            "the-craft-of-research/derived/actionable-principles.md",
            "the-craft-of-research/derived/chapter-principles.md",
            "the-craft-of-research/the-craft-of-research.md",
            "Never invent evidence, quotations, citations, page numbers",
            "The book supplies a research method, not current facts",
            "Do not introduce methods from other frameworks",
        ),
        "Claude Williams agent",
    )

    invalid_aliases = []
    for path in (ROOT / ".claude" / "agents").glob("*.md"):
        agent_text = read_text(path)
        agent_fields = parse_frontmatter(agent_text, str(path.relative_to(ROOT)))
        if agent_fields.get("name") == "_williams":
            invalid_aliases.append(path.relative_to(ROOT))
    check(not invalid_aliases, f"invalid Claude _williams registration(s): {invalid_aliases}")


def validate_runtime_packages(handbook: str) -> None:
    codex_agent = read_text(CODEX_AGENT)
    codex_skill = read_text(CODEX_SKILL)
    codex_reference = read_text(CODEX_REFERENCE)
    codex_interface = read_text(CODEX_INTERFACE)
    grok_agent = read_text(GROK_AGENT)

    if tomllib is not None:
        try:
            parsed_codex_agent = tomllib.loads(codex_agent)
        except tomllib.TOMLDecodeError as error:
            raise ValidationError(f"Codex Williams TOML is invalid: {error}") from error
        check(parsed_codex_agent.get("name") == "_williams", "Codex TOML name must be _williams")
        check(
            parsed_codex_agent.get("sandbox_mode") == "read-only",
            "Codex Williams agent must remain read-only",
        )

    require_fragments(
        codex_agent,
        (
            'name = "_williams"',
            'sandbox_mode = "read-only"',
            ".codex/skills/williams-research-guide/SKILL.md",
            "Never invent evidence, quotations, citations, page numbers",
        ),
        "Codex Williams agent",
    )
    require_fragments(
        codex_skill,
        (
            "name: williams-research-guide",
            "references/actionable-principles.md",
            "I am studying X because I want to find out Y, in order to help my audience understand Z.",
            "Maintain a working argument: a specific and contestable claim",
            "reasons, evidence, warrants where needed",
            "Never invent evidence, quotations, references, page numbers",
        ),
        "Codex Williams skill",
    )
    require_fragments(
        codex_interface,
        ('display_name: "_williams"', "$williams-research-guide"),
        "Codex Williams interface",
    )

    grok_fields = parse_frontmatter(grok_agent, "Grok Williams agent")
    check(grok_fields.get("name") == "_williams", "Grok agent must register as _williams")
    require_fragments(
        grok_agent,
        (
            "You are **_williams**",
            "AP-18 Write the three-part project statement",
            "AP-51 Distinguish claim, reason, evidence",
            "AP-66 Construct a warrant for each reason",
            "AP-121 Keep the integrity floor",
            "_williams-chapter-principles.md",
            "Read the complete handbook for a full research audit",
            "Do not manufacture significance, evidence, quotations, citations, page numbers",
        ),
        "Grok Williams agent",
    )

    check(
        handbook == codex_reference,
        "Codex Williams handbook mirror differs from the canonical handbook "
        f"(canonical {sha256(HANDBOOK)}, mirror {sha256(CODEX_REFERENCE)})",
    )


def validate_installed_grok(ledger: str, handbook: str) -> None:
    installed_agent = read_text(GROK_INSTALLED_AGENT)
    installed_handbook = read_text(GROK_INSTALLED_HANDBOOK)
    installed_ledger = read_text(GROK_INSTALLED_LEDGER)

    check(
        installed_agent == read_text(GROK_AGENT),
        "installed Grok Williams agent differs from the repository agent "
        f"(repo {sha256(GROK_AGENT)}, installed {sha256(GROK_INSTALLED_AGENT)})",
    )
    check(
        installed_handbook == handbook,
        "installed Grok Williams handbook differs from the canonical handbook "
        f"(canonical {sha256(HANDBOOK)}, installed {sha256(GROK_INSTALLED_HANDBOOK)})",
    )
    check(
        installed_ledger == ledger,
        "installed Grok Williams provenance ledger differs from the canonical ledger "
        f"(canonical {sha256(CHAPTER_LEDGER)}, installed {sha256(GROK_INSTALLED_LEDGER)})",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--derived-only",
        action="store_true",
        help="validate derived artifacts and runtime packages without reading the raw corpus",
    )
    parser.add_argument(
        "--skip-installed-grok",
        action="store_true",
        help="skip validation of user-level Grok mirrors",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.derived_only:
            ledger, handbook = load_derived_artifacts()
        else:
            _, _, ledger, handbook = validate_corpus()
        validate_principles(handbook, ledger)
        validate_claude_agent(read_text(CLAUDE_AGENT))
        validate_runtime_packages(handbook)
        if not args.skip_installed_grok:
            validate_installed_grok(ledger, handbook)
    except (OSError, UnicodeError, ValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    scope = "derived artifacts" if args.derived_only else "corpus and derived artifacts"
    installed = " without installed Grok mirrors" if args.skip_installed_grok else ""
    print(f"PASS: _williams {scope}, agents, and mirrors are consistent{installed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
