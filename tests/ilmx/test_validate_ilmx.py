import importlib.util
import json
import pathlib

_spec = importlib.util.spec_from_file_location(
    "validate", pathlib.Path(__file__).resolve().parent.parent.parent / "scripts" / "validate-ilmx.py"
)
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)


def make(root, skill_name="ilmx-x", desc="d"):
    (root / ".claude-plugin").mkdir()
    for name in ("plugin.json", "marketplace.json"):
        (root / ".claude-plugin" / name).write_text(json.dumps({}))
    skill = root / "skills" / "ilmx-x"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {skill_name}\ndescription: {desc}\n---\nbody\n")
    (root / "agents").mkdir()


def test_repo_is_valid():
    assert validate.check() == []


def test_valid_tree(tmp_path):
    make(tmp_path)
    assert validate.check(tmp_path) == []


def test_wrong_name_and_missing_description(tmp_path):
    make(tmp_path, skill_name="y", desc="")
    assert "name must be 'ilmx-x'" in validate.check(tmp_path)[0]


def test_missing_front_matter_and_bad_json(tmp_path):
    make(tmp_path)
    (tmp_path / "agents" / "ilmx-a.md").write_text("no front matter")
    (tmp_path / ".claude-plugin" / "plugin.json").write_text("{")
    errors = validate.check(tmp_path)
    assert any("no front matter" in e for e in errors)
    assert any(e.startswith("plugin.json") for e in errors)


def test_main_exit_codes(tmp_path, capsys):
    assert validate.main() == 0
    assert validate.main(tmp_path) == 1
    assert "plugin.json" in capsys.readouterr().out
