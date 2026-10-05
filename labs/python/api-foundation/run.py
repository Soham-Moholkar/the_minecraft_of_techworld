"""A resettable L0 HTTP-flow lab with no third-party dependencies."""

import json
import pathlib
import sys

STATE = pathlib.Path(__file__).with_name(".state.json")


def run(action: str) -> None:
    if action == "start":
        STATE.write_text(json.dumps({"status": "ready", "endpoint": "/health"}), encoding="utf-8")
        print("ready: trace GET /health in apps/api-python/src/atlas_api/main.py")
    elif action == "test":
        assert STATE.exists(), "start the lab first"
        assert json.loads(STATE.read_text(encoding="utf-8"))["status"] == "ready"
        print("pass: lab state and endpoint contract are valid")
    elif action == "reset":
        STATE.unlink(missing_ok=True)
        print("reset: generated lab state removed")
    else:
        raise ValueError(f"unsupported action: {action}")


if __name__ == "__main__":
    run(sys.argv[1])

