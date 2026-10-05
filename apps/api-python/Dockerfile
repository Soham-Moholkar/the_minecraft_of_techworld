FROM python:3.12.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system atlas && adduser --system --ingroup atlas atlas
COPY apps/api-python /app/apps/api-python
# The runtime receives a curated, read-only source snapshot for repository AI.
# Secrets, Git metadata, dependencies and build outputs are excluded by choosing
# explicit paths instead of copying the build context wholesale.
COPY apps /workspace/apps
COPY content /workspace/content
COPY docs /workspace/docs
COPY infra/airflow /workspace/infra/airflow
COPY infra/spark /workspace/infra/spark
COPY infra/flink /workspace/infra/flink
COPY infra/superset /workspace/infra/superset
COPY infra/helm /workspace/infra/helm
COPY infra/kubernetes /workspace/infra/kubernetes
COPY infra/terraform /workspace/infra/terraform
COPY labs /workspace/labs
COPY packages /workspace/packages
COPY registry /workspace/registry
COPY scripts /workspace/scripts
COPY security /workspace/security
COPY work /workspace/work
COPY README.md compose.yaml package.json pnpm-workspace.yaml /workspace/
ARG ATLAS_NEURAL=false
ARG ATLAS_STREAMING=false
RUN if [ "$ATLAS_STREAMING" = "true" ]; then pip install --no-cache-dir '/app/apps/api-python[streaming]'; fi
ARG ATLAS_LAKEHOUSE=false
RUN if [ "$ATLAS_LAKEHOUSE" = "true" ]; then pip install --no-cache-dir '/app/apps/api-python[lakehouse]'; fi
RUN if [ "$ATLAS_NEURAL" = "true" ]; then pip install --no-cache-dir torch==2.14.0+cpu --index-url https://download.pytorch.org/whl/cpu; fi
RUN if [ "$ATLAS_NEURAL" = "true" ]; then pip install --no-cache-dir tensorflow-cpu==2.21.0 keras==3.15.1; fi
RUN pip install --no-cache-dir '/app/apps/api-python[data]'
RUN chown -R atlas:atlas /workspace
RUN mkdir -p /var/lib/atlas && chown atlas:atlas /var/lib/atlas
USER atlas
EXPOSE 8000
CMD ["sh", "-c", "python -m alembic -c apps/api-python/alembic.ini upgrade head && python -m atlas_api.seed && uvicorn atlas_api.main:app --host 0.0.0.0 --port 8000"]
