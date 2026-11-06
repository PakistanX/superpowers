import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def copy(tmp_path):
    target = tmp_path / "plugins" / "ilmx"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (tmp_path / ".claude-plugin").mkdir()
    shutil.copy(ROOT.parent.parent / ".claude-plugin" / "marketplace.json", tmp_path / ".claude-plugin")
    (tmp_path / "skills").mkdir()
    for upstream in (ROOT.parent.parent / "skills").glob("*/SKILL.md"):
        (tmp_path / "skills" / upstream.parent.name).mkdir()
        (tmp_path / "skills" / upstream.parent.name / "SKILL.md").write_text("x")
    return target


def test_real_plugin_is_valid():
    assert validate.check() == []


def test_main_exit_codes(tmp_path, capsys):
    assert validate.main() == 0
    broken = copy(tmp_path)
    (broken / "hooks" / "hooks.json").write_text("{")
    assert validate.main(broken) == 1
    assert "hooks/hooks.json" in capsys.readouterr().out


def test_agent_rules(tmp_path):
    root = copy(tmp_path)
    agent = root / "agents" / "ilmx-fetcher.md"
    text = agent.read_text()
    agent.write_text(text.replace("model: haiku", "model: inherit").replace("maxTurns: 15", "maxTurns: 0")
                     .replace("effort: low", "effort: max").replace("disallowedTools: Edit, Write, NotebookEdit, Agent",
                                                                     "disallowedTools: Edit"))
    errors = "\n".join(validate.check(root))
    assert "model must be one of" in errors and "maxTurns" in errors and "effort must be" in errors
    assert "workers must list Agent" in errors


def test_front_matter_problems(tmp_path):
    root = copy(tmp_path)
    (root / "agents" / "ilmx-writer.md").write_text("no front matter")
    (root / "agents" / "ilmx-planner.md").write_text("---\n: [bad\n---\nbody")
    (root / "agents" / "ilmx-debugger.md").write_text("---\n- a list\n---\nbody")
    skill = root / "skills" / "ilmx-rules" / "SKILL.md"
    skill.write_text(skill.read_text().replace("name: ilmx-rules", "name: other"))
    errors = "\n".join(validate.check(root))
    assert errors.count("no valid front matter") == 3
    assert "ilmx-rules/SKILL.md: front matter needs name" in errors


def test_unresolved_references(tmp_path):
    root = copy(tmp_path)
    skill = root / "skills" / "ilmx-rules" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nSee `ilmx:nothing` and `superpowers:nothing-either`.\n")
    errors = "\n".join(validate.check(root))
    assert "ilmx:nothing does not resolve" in errors and "superpowers:nothing-either does not resolve" in errors


def test_manifest_and_hook_problems(tmp_path):
    root = copy(tmp_path)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "other"}))
    (root / "hooks" / "guard").chmod(0o644)
    (root / "hooks" / "hooks.json").write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": []}]}}))
    errors = "\n".join(validate.check(root))
    assert "name must be 'ilmx'" in errors and "must exist and be executable" in errors and "no PreToolUse command" in errors
    (root / ".claude-plugin" / "plugin.json").unlink()
    assert ".claude-plugin/plugin.json" in "\n".join(validate.check(root))


def test_comma_separated_tools_are_read():
    assert validate.as_list("Edit, Agent") == ["Edit", "Agent"]
    assert validate.as_list(None) == []


def test_agent_name_must_match_the_file(tmp_path):
    root = copy(tmp_path)
    agent = root / "agents" / "ilmx-writer.md"
    agent.write_text(agent.read_text().replace("name: ilmx-writer", "name: writer"))
    assert "front matter needs name 'ilmx-writer'" in "\n".join(validate.check(root))


def test_marketplace_entry(tmp_path):
    root = copy(tmp_path)
    market = tmp_path / ".claude-plugin" / "marketplace.json"
    original = market.read_text()
    market.write_text(original.replace('"source": "./plugins/ilmx"', '"source": "./plugins/other"'))
    assert "does not point at plugins/ilmx" in "\n".join(validate.check(root))
    market.write_text(original.replace('"name": "ilmx"', '"name": "elsewhere"'))
    assert "no entry named 'ilmx'" in "\n".join(validate.check(root))
    market.write_text("{")
    assert "marketplace.json" in "\n".join(validate.check(root))
    market.unlink()
    assert "marketplace.json" in "\n".join(validate.check(root))


def test_preloaded_skills(tmp_path):
    root = copy(tmp_path)
    planner = root / "agents" / "ilmx-planner.md"
    text = planner.read_text()
    planner.write_text(text.replace("skills: [ilmx-rules,", "skills: [ilmx-missing, ilmx-rules,"))
    assert "skills: ilmx-missing does not resolve" in "\n".join(validate.check(root))
    lines = [line for line in text.splitlines() if not line.startswith("skills:")]
    planner.write_text("\n".join(lines) + "\n")
    assert "a tools allow-list needs Skill or a skills: preload" in "\n".join(validate.check(root))
    planner.write_text(text.replace("tools: Read, Grep, Glob, Bash, Write", "tools: Read, Skill").replace("skills: [", "xskills: ["))
    assert validate.check(root) == []
