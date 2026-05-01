"""Tests for check_project.py."""
import os
import subprocess
import sys
import pytest
import tempfile

# tests/tools/ → project_root/tools/
CHECK_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools", "check_project.py"
)


def run_check(project_dir: str, *flags: str) -> tuple[str, int]:
    """Run check_project.py and return (stdout, exit_code)."""
    result = subprocess.run(
        [sys.executable, CHECK_SCRIPT, project_dir, *flags],
        capture_output=True, text=True, timeout=90,
    )
    return result.stdout, result.returncode


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def _seed_scaffolded_project(project_dir: str):
    """Build a directory tree that satisfies every static --build check.
    Deliberately omits `.claude/godotmaker.yaml` so the headless step
    WARNs and skips the godot subprocess — keeps the test suite fast
    and independent of a real Godot binary.
    """
    # project.godot with [application] + godot-e2e plugin enabled
    with open(os.path.join(project_dir, "project.godot"), "w", encoding="utf-8") as f:
        f.write(
            'config_version=5\n\n'
            '[application]\n'
            'config/name="Test"\n\n'
            '[editor_plugins]\n'
            'enabled=PackedStringArray('
            '"res://addons/gecs/plugin.cfg",'
            '"res://addons/gdunit4/plugin.cfg",'
            '"res://addons/godot_e2e/plugin.cfg"'
            ')\n'
        )
    # Required addon dirs
    for addon in ("gecs", "gdunit4", "godot_e2e"):
        os.makedirs(os.path.join(project_dir, "addons", addon), exist_ok=True)
    # e2e/conftest.py with GodotE2E import
    e2e_dir = os.path.join(project_dir, "e2e")
    os.makedirs(e2e_dir, exist_ok=True)
    with open(os.path.join(e2e_dir, "conftest.py"), "w", encoding="utf-8") as f:
        f.write("from godot_e2e import GodotE2E\n")
    # git repo with one commit
    subprocess.run(["git", "init", "-q"], cwd=project_dir, check=True)
    subprocess.run(["git", "-C", project_dir, "config", "user.email", "x@y.z"], check=True)
    subprocess.run(["git", "-C", project_dir, "config", "user.name", "x"], check=True)
    subprocess.run(["git", "-C", project_dir, "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", project_dir, "commit", "-q", "-m", "init"],
        check=True,
    )


class TestBuildCheck:
    """`--build` is the gm-scaffold readiness check — verifies all of
    Step 4 (project.godot, addons, plugin, conftest, git, headless).
    Headless coverage relies on the WARN-on-missing-godot_path branch:
    tests skip the subprocess by leaving `.claude/godotmaker.yaml`
    out of the seed."""

    def test_no_project_godot(self, project_dir):
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "[FAIL]" in stdout
        assert "project.godot" in stdout

    def test_full_scaffold_passes_static(self, project_dir):
        _seed_scaffolded_project(project_dir)
        stdout, code = run_check(project_dir, "--build")
        assert code == 0, f"expected pass, got:\n{stdout}"
        assert "project.godot exists" in stdout
        assert "[application] section" in stdout
        for addon in ("gecs", "gdunit4", "godot_e2e"):
            assert f"addons/{addon}/ present" in stdout
        assert "godot-e2e plugin enabled" in stdout
        assert "e2e/conftest.py imports GodotE2E" in stdout
        assert "git HEAD resolves" in stdout

    def test_missing_application_section(self, project_dir):
        with open(os.path.join(project_dir, "project.godot"), "w") as f:
            f.write("[rendering]\n")
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "[FAIL]" in stdout
        assert "[application]" in stdout

    def test_missing_addon_directory_fails(self, project_dir):
        _seed_scaffolded_project(project_dir)
        # remove gecs to simulate forgotten addon install
        import shutil
        shutil.rmtree(os.path.join(project_dir, "addons", "gecs"))
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "addons/gecs/ missing" in stdout

    def test_godot_e2e_plugin_not_enabled_fails(self, project_dir):
        _seed_scaffolded_project(project_dir)
        # rewrite project.godot without the godot_e2e plugin entry
        with open(os.path.join(project_dir, "project.godot"), "w", encoding="utf-8") as f:
            f.write(
                'config_version=5\n[application]\nconfig/name="Test"\n\n'
                '[editor_plugins]\nenabled=PackedStringArray("res://addons/gecs/plugin.cfg")\n'
            )
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "godot-e2e plugin not enabled" in stdout

    def test_conftest_without_godote2e_import_fails(self, project_dir):
        _seed_scaffolded_project(project_dir)
        with open(os.path.join(project_dir, "e2e", "conftest.py"), "w", encoding="utf-8") as f:
            f.write("# empty\n")
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "does not import GodotE2E" in stdout

    def test_git_dir_missing_fails(self, project_dir):
        """No .git/ at all — fail with 'missing' message."""
        # Seed enough static state to reach the git check (project.godot
        # exists; addon / plugin / conftest checks fail noisily but don't
        # short-circuit, so the git fail message is still emitted).
        with open(os.path.join(project_dir, "project.godot"), "w", encoding="utf-8") as f:
            f.write('[application]\nconfig/name="Test"\n')
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert ".git/ missing" in stdout

    def test_git_without_head_fails(self, project_dir):
        """`.git/` exists but no commits → HEAD doesn't resolve. Build a
        fresh project (no _seed_scaffolded_project) so we never have to
        rmtree a git-managed `.git/` (Windows holds file handles open
        and rmtree fails with PermissionError)."""
        with open(os.path.join(project_dir, "project.godot"), "w", encoding="utf-8") as f:
            f.write('[application]\nconfig/name="Test"\n')
        subprocess.run(["git", "init", "-q"], cwd=project_dir, check=True)
        stdout, code = run_check(project_dir, "--build")
        assert code == 1
        assert "HEAD does not resolve" in stdout

    def test_headless_skipped_when_godot_path_missing(self, project_dir):
        _seed_scaffolded_project(project_dir)
        # No .claude/godotmaker.yaml — headless check WARNs (not FAILs),
        # so static-only scaffold projects still pass --build with a
        # visible warning instead of being silently broken.
        stdout, code = run_check(project_dir, "--build")
        assert "godot_path missing" in stdout
        assert "[WARN]" in stdout
        assert code == 0  # static checks all passed → overall pass


class TestEcsCheck:
    def test_no_gecs_addon(self, project_dir):
        stdout, code = run_check(project_dir, "--ecs")
        assert code == 1
        assert "[FAIL]" in stdout
        assert "gecs" in stdout

    def test_with_gecs_and_components(self, project_dir):
        os.makedirs(os.path.join(project_dir, "addons", "gecs"))
        comp_dir = os.path.join(project_dir, "components")
        os.makedirs(comp_dir)
        with open(os.path.join(comp_dir, "health.gd"), "w") as f:
            f.write("extends Component\nvar current: int = 100\n")
        sys_dir = os.path.join(project_dir, "systems")
        os.makedirs(sys_dir)
        with open(os.path.join(sys_dir, "movement_system.gd"), "w") as f:
            f.write("extends System\nfunc _process(delta):\n\tpass\n")

        stdout, code = run_check(project_dir, "--ecs")
        assert code == 0
        assert "[PASS]" in stdout


class TestTestsCheck:
    def test_no_gdunit(self, project_dir):
        stdout, code = run_check(project_dir, "--tests")
        assert code == 1
        assert "gdUnit4" in stdout

    def test_system_without_test(self, project_dir):
        os.makedirs(os.path.join(project_dir, "addons", "gdunit4"))
        sys_dir = os.path.join(project_dir, "systems")
        os.makedirs(sys_dir)
        with open(os.path.join(sys_dir, "move.gd"), "w") as f:
            f.write("extends System\n")

        stdout, code = run_check(project_dir, "--tests")
        assert code == 1
        assert "[FAIL]" in stdout
        assert "test" in stdout.lower()

    def test_system_with_test(self, project_dir):
        os.makedirs(os.path.join(project_dir, "addons", "gdunit4"))
        sys_dir = os.path.join(project_dir, "systems")
        os.makedirs(sys_dir)
        with open(os.path.join(sys_dir, "move.gd"), "w") as f:
            f.write("extends System\n")
        test_dir = os.path.join(project_dir, "test")
        os.makedirs(test_dir)
        with open(os.path.join(test_dir, "test_move.gd"), "w") as f:
            f.write("extends GdUnitTestSuite\n")

        stdout, code = run_check(project_dir, "--tests")
        assert code == 0


class TestPlanCheck:
    def test_no_plan(self, project_dir):
        stdout, code = run_check(project_dir, "--plan")
        assert code == 1
        assert "PLAN.md" in stdout

    def test_with_plan_and_structure(self, project_dir):
        with open(os.path.join(project_dir, "PLAN.md"), "w") as f:
            f.write("# Plan\n## Task Status\n| 1 | Move | completed | done |\n")
        with open(os.path.join(project_dir, "STRUCTURE.md"), "w") as f:
            f.write("# Structure\n## Component Registry\n## System Schedule\n")

        stdout, code = run_check(project_dir, "--plan")
        assert code == 0
        assert "[PASS]" in stdout


class TestAllCheck:
    def test_empty_project_fails(self, project_dir):
        stdout, code = run_check(project_dir, "--all")
        assert code == 1
        assert "[FAIL]" in stdout
        assert "Result: CHECKS FAILED" in stdout

    def test_summary_counts(self, project_dir):
        stdout, code = run_check(project_dir, "--all")
        assert "Total:" in stdout
        assert "PASS:" in stdout
        assert "FAIL:" in stdout
