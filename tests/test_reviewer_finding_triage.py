"""Lock in the structural invariants of reviewer-finding-triage.md.

The triage doc is the single source of truth for how build/fixgap handle
reviewer findings (ACCEPT / REJECT / SKIP). It is markdown, so its rules
are LLM-interpreted, not code-enforced — but the rules are load-bearing
enough that we want a regression gate against silent weakening.

These tests check structural properties only (sections exist, three
options present, citation requirement intact, the doc is wired to the
right consumers in the manifest). They do NOT validate LLM behavior.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRIAGE = REPO_ROOT / "skills" / "core" / "_shared" / "reviewer-finding-triage.md"
MANIFEST = REPO_ROOT / "skills" / "core" / "_shared" / "manifest.json"
MEMORY_TEMPLATE = REPO_ROOT / "templates" / "MEMORY.md"


class TestTriageDocExists:
    def test_doc_exists(self):
        assert TRIAGE.exists(), \
            "reviewer-finding-triage.md missing — load-bearing for gm-build/gm-fixgap"

    def test_registered_for_build_and_fixgap(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        consumers = manifest["files"].get("reviewer-finding-triage.md")
        assert consumers is not None, \
            "manifest must register reviewer-finding-triage.md"
        assert "gm-build" in consumers
        assert "gm-fixgap" in consumers


class TestTriageDocStructure:
    """Three options must remain; citation rules must remain intact."""

    def setup_method(self):
        self.content = TRIAGE.read_text(encoding="utf-8")

    def test_has_three_options(self):
        for option in ["ACCEPT", "REJECT", "SKIP"]:
            assert option in self.content, \
                f"triage option '{option}' must remain in the doc"

    def test_defaults_per_severity(self):
        """critical/major default ACCEPT; minor default SKIP."""
        lower = self.content.lower()
        assert "default" in lower
        # The doc must explicitly tie each default to a severity.
        assert "critical / major" in self.content or "critical/major" in self.content
        assert "minor" in self.content

    def test_citation_required_for_critical_major(self):
        """Citation must be required for critical/major REJECT and SKIP."""
        assert "Citation" in self.content or "citation" in self.content
        # Citation source types must remain enumerated.
        for token in ["gotcha", "MEMORY.md", "PLAN.md", "GAP.md"]:
            assert token in self.content, \
                f"citation source '{token}' must remain in the allowed list"
        # The severity-conditional rule must remain.
        assert "Required" in self.content, \
            "doc must mark citation as Required for critical/major"

    def test_forbidden_reasons_listed(self):
        """Common LLM excuses must be explicitly forbidden."""
        for forbidden in ["Code looks correct", "Worker tested it",
                          "Reviewer is wrong"]:
            assert forbidden in self.content, \
                f"'{forbidden}' must remain in the forbidden-reasons list"


class TestMemoryTemplateHasTriageSection:
    def test_section_present(self):
        content = MEMORY_TEMPLATE.read_text(encoding="utf-8")
        assert "## Reviewer Triage Log" in content, \
            "templates/MEMORY.md must keep the Reviewer Triage Log section"

    def test_section_documents_required_fields(self):
        content = MEMORY_TEMPLATE.read_text(encoding="utf-8")
        # Each triage record must document these fields, including Decision
        # so REJECT and SKIP can be distinguished.
        for field in ["Finding:", "Severity:", "Decision:",
                      "Reason:", "Citation:"]:
            assert field in content, \
                f"triage record format must keep field '{field}'"
