import json
import pathlib
import subprocess
import sys

GUARD = pathlib.Path(__file__).resolve().parent.parent / "hooks" / "guard"


def run(agent, tool, **tool_input):
    event = {"agent_type": agent, "tool_name": tool, "tool_input": tool_input}
    return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), text=True, capture_output=True)


def test_orchestrator_and_main_thread_are_unaffected():
    assert run("ilmx:ilmx-orchestrator", "Bash", command="git push origin develop").returncode == 0
    assert run("", "Bash", command="git push origin develop").returncode == 0
    assert run("someone-else", "Bash", command="gh pr create").returncode == 0


def test_workers_cannot_publish_from_the_shell():
    for command in ("git push origin develop", "git push", "gh pr create --title x", "gh pr comment 1 -b hi",
                    "gh issue close 3", "gh release create v1", "gh workflow run ci.yml",
                    "gh api repos/a/b/issues -X POST", "gh api repos/a/b/pulls/1/comments -f body=x"):
        result = run("ilmx:ilmx-implementer", "Bash", command=command)
        assert result.returncode == 2, command
        assert "must not" in result.stderr


def test_workers_can_read_and_run_tests():
    for command in ("git status", "git diff", "gh pr view 1", "gh pr list", "gh api repos/a/b/pulls/1", "pytest -q"):
        assert run("ilmx:ilmx-implementer", "Bash", command=command).returncode == 0, command


def test_workers_cannot_write_to_github_or_taiga():
    for tool in ("mcp__github__create_pull_request", "mcp__github__add_issue_comment", "mcp__github__merge_pull_request",
                 "mcp__taiga__taiga_userstories_update", "mcp__taiga__taiga_userstory_comment_create",
                 "mcp__taiga__taiga_tasks_create", "mcp__taiga__taiga_tasks_delete"):
        assert run("ilmx:ilmx-writer", tool).returncode == 2, tool
    for tool in ("mcp__github__get_pull_request", "mcp__taiga__taiga_userstories_get", "mcp__taiga__taiga_tasks_list",
                 "mcp__taiga__taiga_search"):
        assert run("ilmx:ilmx-fetcher", tool).returncode == 0, tool


def test_workers_cannot_spawn_agents():
    assert run("ilmx:ilmx-planner", "Agent", prompt="x").returncode == 2


def test_file_writes_are_limited_to_each_workers_output():
    assert run("ilmx:ilmx-planner", "Write", file_path="/p/plans/feature.md").returncode == 0
    assert run("ilmx:ilmx-planner", "Write", file_path="/repo/src/app.py").returncode == 2
    assert run("ilmx:ilmx-parity-auditor", "Write", file_path="/p/inventories/f.md").returncode == 0
    assert run("ilmx:ilmx-parity-auditor", "Edit", file_path="/repo/x.py").returncode == 2
    assert run("ilmx:ilmx-reviewer", "Write", file_path="/work/findings.json").returncode == 0
    assert run("ilmx:ilmx-reviewer", "Write", file_path="/work/other.txt").returncode == 2
    assert run("ilmx:ilmx-debugger", "Write", file_path="/p/plans/x.md").returncode == 2
    assert run("ilmx:ilmx-fetcher", "Write", file_path="/p/plans/x.md").returncode == 2
    for worker in ("ilmx-implementer", "ilmx-parity-tester", "ilmx-writer"):  # these write code, tests and drafts
        assert run(f"ilmx:{worker}", "Write", file_path="/repo/src/app.py").returncode == 0, worker
