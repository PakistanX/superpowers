"""Validate the ilmx plugin: manifests, agent frontmatter, skills, skill references and the guard hook."""
import json
import os
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MODELS = {"opus", "sonnet", "haiku"}
EFFORTS = {"low", "medium", "high"}
ORCHESTRATOR = "ilmx-orchestrator"
REFERENCE = re.compile(r"`(ilmx|superpowers):([a-z0-9-]+)`")


def frontmatter(path):
    match = FRONT.match(path.read_text())
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def as_list(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return list(value or [])


def check(root=ROOT, upstream_skills=None):
    """Return a list of problems; empty means valid. `upstream_skills` is the upstream skills directory."""
    errors = []
    if upstream_skills is None:
        upstream_skills = root.parent.parent / "skills"
    for rel in (".claude-plugin/plugin.json",):
        try:
            data = json.loads((root / rel).read_text())
            if data.get("name") != "ilmx":
                errors.append(f"{rel}: name must be 'ilmx'")
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")

    skills = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    agents = {p.stem for p in (root / "agents").glob("*.md")}
    bodies = []

    for path in sorted((root / "skills").glob("*/SKILL.md")):
        data = frontmatter(path)
        if data is None or data.get("name") != path.parent.name or not data.get("description"):
            errors.append(f"{path.relative_to(root)}: front matter needs name '{path.parent.name}' and a description")
        bodies.append((path, path.read_text()))

    for path in sorted((root / "agents").glob("*.md")):
        rel = path.relative_to(root)
        data = frontmatter(path)
        if data is None:
            errors.append(f"{rel}: no valid front matter")
            continue
        if data.get("name") != path.stem or not data.get("description"):
            errors.append(f"{rel}: front matter needs name '{path.stem}' and a description")
        if data.get("model") not in MODELS:
            errors.append(f"{rel}: model must be one of {sorted(MODELS)}, not {data.get('model')!r}")
        if data.get("effort") not in EFFORTS:
            errors.append(f"{rel}: effort must be one of {sorted(EFFORTS)}")
        turns = data.get("maxTurns")
        if not isinstance(turns, int) or turns <= 0:
            errors.append(f"{rel}: maxTurns must be a positive integer")
        if path.stem != ORCHESTRATOR and "Agent" not in as_list(data.get("disallowedTools")):
            errors.append(f"{rel}: workers must list Agent in disallowedTools")
        bodies.append((path, path.read_text()))

    for path, text in bodies:
        for namespace, name in REFERENCE.findall(text):
            known = skills | agents if namespace == "ilmx" else {p.parent.name for p in upstream_skills.glob("*/SKILL.md")}
            if name not in known:
                errors.append(f"{path.relative_to(root)}: {namespace}:{name} does not resolve")

    hooks = root / "hooks"
    try:
        config = json.loads((hooks / "hooks.json").read_text())
        commands = [h["command"] for entry in config["hooks"]["PreToolUse"] for h in entry["hooks"]]
        if not commands:
            errors.append("hooks/hooks.json: no PreToolUse command")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"hooks/hooks.json: {exc}")
    guard = hooks / "guard"
    if not guard.is_file() or not os.access(guard, os.X_OK):
        errors.append("hooks/guard must exist and be executable")
    return errors


def main(root=ROOT):
    problems = check(root)
    print("\n".join(problems) or "ok")
    return 1 if problems else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
