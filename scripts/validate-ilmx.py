"""Check the ilmX additions: manifests parse, every ilmx-* skill and agent has a matching name and a description."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def front_matter(path):
    match = FRONT.match(path.read_text())
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def check(root=ROOT):
    errors = []
    for name in ("plugin.json", "marketplace.json"):
        try:
            json.loads((root / ".claude-plugin" / name).read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{name}: {exc}")
    files = list((root / "skills").glob("ilmx-*/SKILL.md")) + list((root / "agents").glob("ilmx-*.md"))
    for path in files:
        fields = front_matter(path)
        expected = path.parent.name if path.name == "SKILL.md" else path.stem
        if fields is None:
            errors.append(f"{path.relative_to(root)}: no front matter")
        elif fields.get("name") != expected or not fields.get("description"):
            errors.append(f"{path.relative_to(root)}: name must be '{expected}' and description set")
    return errors


def main(root=ROOT):
    problems = check(root)
    print("\n".join(problems) or "ok")
    return 1 if problems else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
