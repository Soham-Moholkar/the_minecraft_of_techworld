"""Real API → typed Parquet → local Spark → receipt/status acceptance.

Uses a unique, owned output fixture and a private loopback API. Requires the
optional compute extra and a configured Java runtime. It never substitutes a
Python aggregate for Spark or claims that local mode verifies a cluster.
"""

import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    folder = (ROOT / "output" / f"spark-acceptance-{uuid4().hex}").resolve()
    folder.mkdir(parents=True)
    # Port allocation is local only; readiness also checks the child process so
    # a port race fails closed instead of accidentally using an existing API.
    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]
    token = "spark-fixture-" + uuid4().hex
    env = os.environ.copy()
    spark_package = importlib.util.find_spec("pyspark")
    if spark_package is None or spark_package.origin is None:
        raise RuntimeError("optional compute extra is unconfigured")
    # Bypass upstream .cmd Python discovery, which splits executable paths
    # containing spaces. This is scoped to the owned acceptance child process.
    env["SPARK_HOME"] = str(Path(spark_package.origin).parent)
    portable_java = ROOT / ".tools/jdk-21.0.12.1+1-jre"
    if not env.get("JAVA_HOME") and (portable_java / "bin/java.exe").exists():
        env["JAVA_HOME"] = str(portable_java)
    env.update(
        {
            "ATLAS_DATABASE_URL": f"sqlite:///{(folder / 'app.db').as_posix()}",
            "ATLAS_STREAMING_STORE": str(folder / "stream.db"),
            "ATLAS_STREAMING_ENABLED": "true",
            "ATLAS_STREAMING_PROVIDER": "sqlite",
            "ATLAS_USAGE_COMPUTE_ENABLED": "true",
            "ATLAS_USAGE_COMPUTE_STORE": str(folder / "compute"),
            "ATLAS_DEV_TOKEN": token,
            "ATLAS_ENVIRONMENT": "development",
            "ATLAS_PIPELINE_ENABLED": "true",
            "ATLAS_PIPELINE_API_TOKEN": token,
            "ATLAS_PIPELINE_API_URL": f"http://127.0.0.1:{port}",
            "ATLAS_PIPELINE_TENANT": "northstar",
            "PYTHONPATH": str(ROOT / "infra/airflow/dags"),
            "PYSPARK_PYTHON": sys.executable,
            "SPARK_LOCAL_IP": "127.0.0.1",
            "PYSPARK_SUBMIT_ARGS": "--master local[2] --conf spark.ui.enabled=false --conf spark.sql.shuffle.partitions=2 pyspark-shell",
        }
    )
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    api = None
    evidence = ROOT / "output/phase10-spark-runtime.log"
    try:
        with evidence.open("w", encoding="utf8") as log:
            api = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "atlas_api.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}",
                headers={"Authorization": "Bearer " + token},
                trust_env=False,
                timeout=15,
            ) as client:
                ready = False
                for _ in range(100):
                    if api.poll() is not None:
                        raise RuntimeError("isolated API stopped before readiness")
                    try:
                        if client.get("/health").status_code == 200:
                            ready = True
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.1)
                if not ready:
                    raise RuntimeError("isolated API readiness timeout")
                response = client.post(
                    "/v1/streaming/usage/events",
                    json={
                        "events": [
                            {"event_id": "first", "units": 4},
                            {"event_id": "second", "units": 3},
                        ]
                    },
                )
                response.raise_for_status()
                client.post(
                    "/v1/streaming/usage/consume", json={"limit": 10}
                ).raise_for_status()
                subprocess.run(
                    [sys.executable, str(ROOT / "infra/spark/usage_job.py")],
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=240,
                    check=True,
                    creationflags=creationflags,
                )
                result = client.get("/v1/pipelines/usage/compute")
                result.raise_for_status()
                value = result.json()
                assert value["source_current"] is True
                assert (
                    value["receipt"]["rows"],
                    value["receipt"]["units"],
                    value["receipt"]["mode"],
                ) == (2, 7, "local")
                # A later accepted effect must make an old successful job stale.
                client.post(
                    "/v1/streaming/usage/events",
                    json={"events": [{"event_id": "third", "units": 1}]},
                ).raise_for_status()
                client.post(
                    "/v1/streaming/usage/consume", json={"limit": 10}
                ).raise_for_status()
                assert (
                    client.get("/v1/pipelines/usage/compute").json()["source_current"]
                    is False
                )
                print(
                    json.dumps(
                        {
                            "provider": "spark",
                            "rows": 2,
                            "units": 7,
                            "mode": "local",
                            "stale_detection": True,
                        }
                    )
                )
    finally:
        if api is not None:
            if os.name == "nt" and api.poll() is None:
                # A Windows venv redirector can own the real interpreter child.
                # End only this still-live, owned process tree before deleting
                # its SQLite files; killing the redirector alone can leak it.
                subprocess.run(
                    ["taskkill", "/PID", str(api.pid), "/T", "/F"],
                    capture_output=True,
                    timeout=10,
                    check=True,
                    creationflags=creationflags,
                )
            else:
                api.terminate()
            try:
                api.wait(timeout=10)
            except subprocess.TimeoutExpired:
                api.kill()
                api.wait(timeout=10)
        # Delete only this unique fixture after the process releases its files.
        if (
            folder.name.startswith("spark-acceptance-")
            and folder.parent == (ROOT / "output").resolve()
            and not folder.is_symlink()
        ):
            # Windows/OneDrive may retain a sharing handle briefly after wait()
            # confirms process exit. Retry only that transient condition; never
            # suppress a persistent lock, permission error or failed teardown.
            for attempt in range(6):
                try:
                    shutil.rmtree(folder)
                    break
                except OSError as exc:
                    if getattr(exc, "winerror", None) != 32 or attempt == 5:
                        raise
                    time.sleep(0.2 * (attempt + 1))


if __name__ == "__main__":
    main()
