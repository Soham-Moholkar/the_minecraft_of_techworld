"""Typed runtime configuration with safe local defaults."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment configuration shared by adapters and HTTP boundaries."""

    model_config = SettingsConfigDict(env_prefix="ATLAS_", env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./atlas.db"
    # This read-only comparison connection never crosses the API boundary. A
    # SecretStr also prevents accidental disclosure through settings repr/logging.
    mariadb_observer_url: SecretStr | None = None
    # MongoDB holds an optional derived projection, never authoritative project
    # state. Keeping its URL secret prevents credentials entering logs or OpenAPI.
    mongodb_projection_url: SecretStr | None = None
    # Redis is an optional acceleration layer. PostgreSQL remains authoritative
    # and every cache call must degrade to a relational read when it is absent.
    redis_cache_url: SecretStr | None = None
    allowed_origins: str = "http://localhost:3000"
    dev_token: str = Field(default="atlas-local-development-token", min_length=16)
    realtime_ticket_ttl_seconds: int = Field(default=30, ge=5, le=300)
    realtime_max_connections: int = Field(default=32, ge=1, le=10_000)
    realtime_max_message_bytes: int = Field(default=2048, ge=128, le=1_048_576)
    realtime_messages_per_window: int = Field(default=10, ge=1, le=10_000)
    realtime_rate_window_seconds: int = Field(default=10, ge=1, le=300)
    # The repository view is read-only and independently path-allowlisted. Images
    # set this to /workspace; local runs resolve it from the repository root.
    repository_root: str = "."
    deployment_review_enabled: bool = False
    infrastructure_plan_enabled: bool = False
    openai_api_key: SecretStr | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    # Local runtimes are opt-in because an OpenAI-compatible URL can point at a
    # powerful workstation service. The URL and model come only from operator
    # configuration; callers cannot turn this boundary into an SSRF primitive.
    local_ai_enabled: bool = False
    local_ai_base_url: str = "http://host.docker.internal:11434/v1"
    local_ai_model: str = "atlas-local-code-model"
    local_ai_api_key: SecretStr | None = None
    # Callers select a cost tier, never an arbitrary provider model identifier.
    ai_economy_model: str = "gpt-5.6-luna"
    ai_balanced_model: str = "gpt-5.6-terra"
    # Hosted inference receives a conservative reservation before the provider
    # call. Actual cost replaces it after success; failed calls release it.
    ai_monthly_budget_usd: float = Field(default=25.0, gt=0, le=100_000)
    ai_run_reservation_usd: float = Field(default=0.25, gt=0, le=100)
    ai_reservation_ttl_seconds: int = Field(default=900, ge=60, le=3_600)
    ai_slo_availability_target: float = Field(default=0.99, gt=0, le=1)
    ai_slo_p95_seconds_target: float = Field(default=30.0, gt=0, le=300)
    # Phase 9 deliberately requires an operator opt-in. This capability is only
    # designed for a trusted local checkout; remote/multi-user execution needs a
    # sandbox and production identity system before this guard may be relaxed.
    ai_patch_tools_enabled: bool = False
    ai_patch_max_file_bytes: int = Field(default=256_000, ge=1_024, le=1_000_000)
    ai_patch_max_changed_lines: int = Field(default=200, ge=1, le=2_000)
    # Test execution is a second, stronger opt-in. The API only queues reviewed
    # profiles; a separate worker enforces the container isolation policy.
    ai_test_tools_enabled: bool = False
    # Independent local opt-in; request data cannot select paths, brokers or topics.
    streaming_enabled: bool = False
    streaming_provider: Literal["sqlite", "kafka"] = "sqlite"
    streaming_store: str = "./atlas-streaming.db"
    kafka_bootstrap: str = "127.0.0.1:59092"
    airflow_enabled: bool = False
    airflow_api_url: str = "http://127.0.0.1:58080"
    airflow_api_token: SecretStr | None = None
    airflow_tenant: str = Field(default="northstar", pattern=r"^[a-z][a-z0-9-]{0,47}$")
    lakehouse_enabled: bool = False
    lakehouse_store: str = "./artifacts/usage-lakehouse"
    usage_compute_enabled: bool = False
    usage_compute_store: str = "./artifacts/usage-compute"
    flink_enabled: bool = False
    flink_api_url: str = "http://127.0.0.1:58081"
    flink_tenant: str = Field(default="northstar", pattern=r"^[a-z][a-z0-9-]{0,47}$")
    flink_job_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")
    superset_enabled: bool = False
    superset_api_url: str = "http://127.0.0.1:58088"
    superset_api_token: SecretStr | None = None
    superset_dashboard_id: int | None = Field(default=None, ge=1, le=2147483647)
    superset_tenant: str = Field(default="northstar", pattern=r"^[a-z][a-z0-9-]{0,47}$")

    @field_validator(
        "openai_api_key",
        "local_ai_api_key",
        "airflow_api_token",
        "flink_job_id",
        "superset_api_token",
        "superset_dashboard_id",
        mode="before",
    )
    @classmethod
    def blank_openai_key_is_unconfigured(cls, value: object) -> object:
        """Compose expands an unset optional variable to an empty string."""
        return None if value == "" else value

    @property
    def origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cache immutable process configuration to keep request behavior stable."""

    return Settings()
