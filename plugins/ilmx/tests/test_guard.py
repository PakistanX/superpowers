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
    for command in ("git push origin develop", "git push", "git -C ../ilmx-features-app push", "git -c x=y push origin x",
                    "git --git-dir=../r/.git push", "git subtree push --prefix=a b main",
                    "cd repo && git push", "echo hi; git push", "env GIT_X=1 git push",
                    "gh pr create --title x", "gh pr comment 1 -b hi", "gh -R PakistanX/x pr create",
                    "gh --repo PakistanX/x pr merge 3", "gh pr review 3 --approve", "gh issue close 3",
                    "gh release create v1", "gh release upload v1 f.zip", "gh workflow run ci.yml", "gh run rerun 5",
                    "gh run cancel 5", "gh repo sync", "gh api repos/a/b/issues -X POST", "gh api -XPOST repos/a/b/issues",
                    "gh api --method=PUT repos/a/b", "gh api repos/a/b/pulls/1/comments -f body=x",
                    "gh api repos/a/b/pulls/1/comments -fbody=x", "gh api graphql -F query=@q.graphql",
                    "curl -H 'Authorization: token t' https://api.github.com/repos/a/b/issues -d '{}'",
                    "wget --post-data=x https://api.github.com/x"):
        result = run("ilmx:ilmx-implementer", "Bash", command=command)
        assert result.returncode == 2, command
        assert "must not" in result.stderr


def test_workers_can_read_and_run_tests():
    for command in ("git status", "git diff", "git -C ../repo log --oneline", "git log --grep push", "git commit -m x",
                    "gh pr view 1", "gh pr list", "gh -R a/b pr diff 3", "gh run view 5 --log", "gh pr checks 3",
                    "gh search issues x", "gh status", "gh --version", "gh api repos/a/b/pulls/1",
                    "gh api repos/a/b/pulls -X GET", "gh api --method GET repos/a/b", "gh api -XGET repos/a/b",
                    "curl -s https://example.org/x", "pytest -q", "echo done", "ls 'unterminated"):
        assert run("ilmx:ilmx-implementer", "Bash", command=command).returncode == 0, command


def test_read_only_workers_cannot_change_files_from_the_shell():
    for command in ("echo x > f.txt", "echo x >> f.txt", "cat a | tee b", "sed -i s/a/b/ f", "sed --in-place s/a/b/ f",
                    "rm -rf build", "git commit -m x", "git -C r checkout main", "git reset --hard", "touch f", "mv a b"):
        for agent in ("ilmx:ilmx-debugger", "ilmx:ilmx-fetcher"):
            assert run(agent, "Bash", command=command).returncode == 2, (agent, command)
    for command in ("git log -3", "git diff", "pytest -q 2>&1 | tail", "ls > /dev/null", "grep x f 2>/dev/null",
                    "sed -n 1,5p f", "cat f"):
        assert run("ilmx:ilmx-debugger", "Bash", command=command).returncode == 0, command


def test_workers_cannot_write_to_github_or_taiga():
    for tool in ("mcp__github__create_pull_request", "mcp__github__add_issue_comment", "mcp__github__merge_pull_request",
                 "mcp__github__issue_write", "mcp__github__pull_request_review_write",
                 "mcp__github__submit_pending_pull_request_review", "mcp__github__run_workflow",
                 "mcp__github__rerun_workflow_run", "mcp__github__request_copilot_review",
                 "mcp__plugin_x_github__issue_write", "mcp__claude_ai_GitHub__create_pull_request",
                 "mcp__taiga__taiga_userstories_update", "mcp__taiga__taiga_userstory_comment_create",
                 "mcp__taiga__taiga_tasks_create", "mcp__taiga__taiga_tasks_delete", "mcp__taiga__taiga_create_userstory",
                 "mcp__taiga__taiga_change_status", "mcp__taiga__taiga_assign_task", "mcp__taiga__taiga_epics_watch",
                 "mcp__taiga__taiga_epics_related_userstories_add", "mcp__plugin_y_taiga__taiga_tasks_update",
                 "mcp__other__taiga_tasks_update"):
        assert run("ilmx:ilmx-writer", tool).returncode == 2, tool
    for tool in ("mcp__github__get_pull_request", "mcp__github__list_issues", "mcp__github__search_code",
                 "mcp__github__issue_read", "mcp__github__pull_request_read", "mcp__claude_ai_GitHub__get_file_contents",
                 "mcp__taiga__taiga_userstories_get", "mcp__taiga__taiga_tasks_list", "mcp__taiga__taiga_search",
                 "mcp__taiga__taiga_users_me", "mcp__taiga__taiga_userstory_history",
                 "mcp__taiga__taiga_epics_related_userstories_list", "mcp__taiga__taiga_epics_watchers",
                 "mcp__slack__send_message", "mcp__short"):
        assert run("ilmx:ilmx-fetcher", tool).returncode == 0, tool


def test_an_event_that_cannot_be_read_is_denied():
    for raw in ("", "not json", "[1]", json.dumps({"agent_type": "ilmx:ilmx-writer", "tool_name": "Bash", "tool_input": "x"})):
        result = subprocess.run([sys.executable, str(GUARD)], input=raw, text=True, capture_output=True)
        assert result.returncode == 2, raw
        assert "could not read" in result.stderr


def test_a_missing_tool_input_is_treated_as_empty():
    event = {"agent_type": "ilmx:ilmx-writer", "tool_name": "Bash", "tool_input": None}
    result = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), text=True, capture_output=True)
    assert result.returncode == 0


def test_workers_cannot_spawn_agents():
    assert run("ilmx:ilmx-planner", "Agent", prompt="x").returncode == 2
    assert run("ilmx:ilmx-planner", "Task", prompt="x").returncode == 2


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


def test_paths_are_resolved_before_they_are_checked():
    assert run("ilmx:ilmx-planner", "Write", file_path="/x/plans/../../repo/app.py").returncode == 2
    assert run("ilmx:ilmx-reviewer", "Write", file_path="/work/../repo/findings.json.py").returncode == 2
    assert run("ilmx:ilmx-planner", "NotebookEdit", notebook_path="/repo/n.ipynb").returncode == 2


def test_relative_paths_use_the_working_directory():
    event = {"agent_type": "ilmx:ilmx-planner", "tool_name": "Write", "cwd": "/p/plans", "tool_input": {"file_path": "f.md"}}
    ok = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), text=True, capture_output=True)
    assert ok.returncode == 0
    event["cwd"] = "/repo"
    bad = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), text=True, capture_output=True)
    assert bad.returncode == 2
