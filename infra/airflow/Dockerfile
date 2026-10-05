# Apache-2.0 upstream runtime; ATLAS owns the DAG and task source.
FROM apache/airflow:3.3.2-python3.12
RUN pip install --no-cache-dir "apache-airflow==3.3.2" "pyarrow==25.0.1"
COPY --chown=airflow:root infra/airflow/dags/ /opt/airflow/dags/
ENV PYTHONPATH=/opt/airflow/dags
