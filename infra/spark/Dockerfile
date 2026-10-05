# Official ASF Spark/Temurin runtime; native Arrow validates the source envelope.
FROM spark:4.2.0-scala2.13-java21-python3-ubuntu
USER root
RUN pip install --break-system-packages --no-cache-dir "pyarrow==25.0.1" && mkdir -p /var/lib/atlas-compute && chown spark:root /var/lib/atlas-compute
COPY --chown=spark:root infra/spark/usage_job.py /opt/atlas/usage_job.py
COPY --chown=spark:root infra/airflow/dags/atlas_usage_tasks.py /opt/atlas/atlas_usage_tasks.py
ENV PYTHONPATH=/opt/atlas
USER spark
ENTRYPOINT []
