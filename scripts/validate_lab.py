"""Dependency-free manifest validation used before any lab command executes."""

import json
import pathlib
import sys

REQUIRED = {"id", "title", "domain", "runtime", "difficulty", "commands", "safety", "resources"}


def validate(path: pathlib.Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED - document.keys()
    if missing:
        raise ValueError(f"missing required keys: {', '.join(sorted(missing))}")
    if document["safety"].get("internet_access_required"):
        raise ValueError("foundation labs must be offline-safe")
    if not {"start", "test", "reset"} <= document["commands"].keys():
        raise ValueError("lab must define start, test, and reset commands")
    print(f"valid: {document['id']} ({document['runtime']})")


if __name__ == "__main__":
    validate(pathlib.Path(sys.argv[1]).resolve())

