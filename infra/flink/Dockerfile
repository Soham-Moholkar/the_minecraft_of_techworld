# Official Apache-2.0 Flink runtime. PyFlink stays isolated from the API venv.
FROM flink:2.3.0-scala_2.12-java17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
# PyFlink 2.3 requires Beam <=2.61, which caps Arrow <17. Keep this dependency
# graph isolated; the API/Spark environments retain Arrow 25.0.1.
RUN python3 -m venv /opt/pyflink && /opt/pyflink/bin/pip install --no-cache-dir "apache-flink==2.3.0" "apache-beam==2.61.0" "pyarrow==16.1.0"
COPY --chown=flink:flink infra/flink/usage_job.py /opt/atlas/usage_flink_job.py
COPY --chown=flink:flink infra/spark/usage_job.py /opt/atlas/usage_job_input.py
COPY --chown=flink:flink infra/airflow/dags/atlas_usage_tasks.py /opt/atlas/atlas_usage_tasks.py
ENV PATH=/opt/pyflink/bin:$PATH PYTHONPATH=/opt/atlas
USER flink
