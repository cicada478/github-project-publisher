from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "github-project-publisher"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_ui_metadata(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: github-project-publisher", frontmatter)
        self.assertRegex(frontmatter, r"(?m)^description: \S")

        ui = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$github-project-publisher", ui)
        self.assertIn("allow_implicit_invocation: true", ui)

    def test_local_markdown_links_resolve(self) -> None:
        markdown_files = [ROOT / "README.md", ROOT / "README.en.md", ROOT / "RELEASE_NOTES.md"]
        markdown_files.extend(SKILL.rglob("*.md"))
        markdown_files.extend((ROOT / "evals").glob("*.md"))
        missing: list[str] = []
        for document in markdown_files:
            text = document.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = target.split("#", 1)[0].replace("%20", " ")
                if path_text and not (document.parent / path_text).resolve().exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
