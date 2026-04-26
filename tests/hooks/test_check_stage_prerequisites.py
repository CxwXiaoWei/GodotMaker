"""Tests for check_stage_prerequisites.py hook (role-based pipeline).

This hook only enforces for build/fixgap roles before Agent dispatch.
It checks that the prerequisite role is completed and its outputs exist.
"""
import os
import shutil
import pytest
import tempfile
from .helpers import (
    run_hook, is_blocked, cleanup_metrics,
    write_completed_roles, write_current_role,
)

SCHEMA_SRC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "stage_schemas.json"
)

HOOK = "check_stage_prerequisites.py"

AGENT_INPUT = {
    "tool_name": "Agent",
    "tool_input": {"prompt": "implement player"},
    "agent_id": "",
}


@pytest.fixture(autouse=True)
def clean():
    yield
    cleanup_metrics()


@pytest.fixture
def project_dir():
    """Create a temp directory with role-based stage_schemas.json and chdir."""
    original = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.makedirs(".godotmaker", exist_ok=True)
        shutil.copy(SCHEMA_SRC, ".godotmaker/stage_schemas.json")
        yield tmpdir
        os.chdir(original)


class TestRoleSkipping:
    @pytest.mark.parametrize("role", ["setup", "verify", "evaluate", "accept", "finalize"])
    def test_non_dispatch_roles_pass_through(self, project_dir, role):
        write_current_role(role)
        _, code, parsed = run_hook(HOOK, AGENT_INPUT)
        assert code == 0
        assert not is_blocked(parsed)

    def test_no_role_passes_through(self, project_dir):
        _, code, parsed = run_hook(HOOK, AGENT_INPUT)
        assert code == 0
        assert not is_blocked(parsed)


class TestBuildPrerequisites:
    def test_block_when_setup_not_complete(self, project_dir):
        write_current_role("build")
        # No completed roles
        _, _, parsed = run_hook(HOOK, AGENT_INPUT)
        assert is_blocked(parsed)
        assert "setup" in parsed.get(
            "hookSpecificOutput", {}).get("permissionDecisionReason", "").lower()

    def test_block_when_setup_complete_but_files_missing(self, project_dir):
        write_current_role("build")
        write_completed_roles(["setup"])
        _, _, parsed = run_hook(HOOK, AGENT_INPUT)
        assert is_blocked(parsed)

    def test_allow_when_setup_files_present(self, project_dir):
        write_current_role("build")
        write_completed_roles(["setup"])
        for f in ["GDD.md", "PLAN.md", "STRUCTURE.md"]:
            open(f, "w").close()
        _, code, parsed = run_hook(HOOK, AGENT_INPUT)
        assert code == 0
        assert not is_blocked(parsed)


class TestFixgapPrerequisites:
    def test_block_when_evaluate_not_complete(self, project_dir):
        write_current_role("fixgap")
        write_completed_roles(["setup", "build", "verify"])  # no evaluate
        _, _, parsed = run_hook(HOOK, AGENT_INPUT)
        assert is_blocked(parsed)

    def test_block_when_evaluation_json_missing(self, project_dir):
        write_current_role("fixgap")
        write_completed_roles(["setup", "build", "verify", "evaluate"])
        # but no evaluation.json
        _, _, parsed = run_hook(HOOK, AGENT_INPUT)
        assert is_blocked(parsed)

    def test_allow_when_evaluation_complete(self, project_dir):
        write_current_role("fixgap")
        write_completed_roles(["setup", "build", "verify", "evaluate"])
        with open(".godotmaker/evaluation.json", "w") as f:
            f.write('{"result": "reject"}')
        _, code, parsed = run_hook(HOOK, AGENT_INPUT)
        assert code == 0
        assert not is_blocked(parsed)


class TestNonAgentTool:
    def test_write_tool_ignored(self, project_dir):
        write_current_role("build")
        _, code, parsed = run_hook(HOOK, {
            "tool_name": "Write",
            "tool_input": {"file_path": "foo.gd"},
            "agent_id": "",
        })
        assert code == 0
        assert not is_blocked(parsed)

    def test_subagent_dispatch_ignored(self, project_dir):
        write_current_role("build")
        _, code, parsed = run_hook(HOOK, {
            "tool_name": "Agent",
            "tool_input": {"prompt": "verify build"},
            "agent_id": "worker-123",
        })
        assert code == 0
        assert not is_blocked(parsed)
