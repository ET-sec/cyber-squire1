"""Squire runtime settings loaded from Doppler-backed env vars.

All secret values arrive via environment (Doppler in prod, local shell in dev).
Never write a default for a real secret; placeholder defaults exist only so
tests can import the module without a live secret store.
"""
from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    # Database (Postgres; name and host come from env, see Doppler)
    cd_db_user: str = Field(..., alias="CD_DB_USER")
    cd_db_pass: SecretStr = Field(..., alias="CD_DB_PASS")
    cd_db_name: str = Field(..., alias="CD_DB_NAME")
    cd_db_host: str = Field("cd-service-db", alias="CD_DB_HOST")
    cd_db_port: int = Field(5432, alias="CD_DB_PORT")

    # Langfuse
    langfuse_public_key: SecretStr = Field(..., alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: SecretStr = Field(..., alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field("http://localhost:3000", alias="LANGFUSE_HOST")
    langfuse_project_id: str | None = Field(None, alias="LANGFUSE_PROJECT_ID")

    # Claude / OpenClaw
    anthropic_api_key: SecretStr = Field(..., alias="ANTHROPIC_API_KEY")
    openclaw_anthropic_key: SecretStr | None = Field(None, alias="OPENCLAW_ANTHROPIC_KEY")
    openclaw_gateway_url: str = Field("http://172.17.0.1:18789", alias="OPENCLAW_GATEWAY_URL")
    claude_model_primary: str = Field("anthropic/claude-fable-5", alias="SQUIRE_MODEL_PRIMARY")
    claude_model_secondary: str = Field("anthropic/claude-opus-5", alias="SQUIRE_MODEL_SECONDARY")

    # Webhook auth
    squire_webhook_token: SecretStr = Field(..., alias="SQUIRE_WEBHOOK_TOKEN")

    # Actions allow-list
    actions_allowlist_path: str = Field(
        "/app/config/actions.yml", alias="SQUIRE_ACTIONS_ALLOWLIST_PATH"
    )

    # Dedup
    dedup_redis_url: str = Field(
        "redis://cd-service-langfuse-redis:6379/1", alias="SQUIRE_DEDUP_REDIS_URL"
    )
    dedup_redis_password: SecretStr | None = Field(None, alias="LANGFUSE_REDIS_PASSWORD")
    dedup_window_seconds: int = Field(300, alias="SQUIRE_DEDUP_WINDOW_SECONDS")

    # Cost ceiling
    anthropic_daily_ceiling_usd: float = Field(5.0, alias="ANTHROPIC_DAILY_CEILING_USD")
    cost_breach_mode: str = Field("ollama", alias="SQUIRE_COST_BREACH_MODE")  # ollama | refuse | warn_only

    # LLM backend selector
    squire_llm_backend: str = Field("api", alias="SQUIRE_LLM_BACKEND")  # api | max | nemo | ollama

    # NeMo Guardrails sidecar (17-10)
    nemo_enabled: bool = Field(False, alias="NEMO_ENABLED")
    nemo_base_url: str = Field(
        "http://cd-service-nemo:8000/v1", alias="NEMO_BASE_URL"
    )
    nemo_config_id: str = Field("default", alias="NEMO_CONFIG_ID")
    nemo_timeout_s: float = Field(60.0, alias="NEMO_TIMEOUT_SECONDS")

    # Graph caps (17-08b)
    max_critique_iterations: int = Field(3, alias="SQUIRE_MAX_CRITIQUE_ITERATIONS")
    max_invocation_seconds: float = Field(30.0, alias="SQUIRE_MAX_INVOCATION_SECONDS")
    max_invocation_cost_usd: float = Field(0.50, alias="SQUIRE_MAX_INVOCATION_COST_USD")

    # Telegram routing for HIGH/CRITICAL severity (17-08b).
    # Both values must be provided via env (Doppler in prod). No real
    # production defaults baked in; the placeholders below exist only so
    # tests can import the module without a live secret store.
    telegram_webhook_url: str = Field(
        "https://example.invalid/webhook/placeholder",
        alias="SQUIRE_TELEGRAM_WEBHOOK_URL",
    )
    telegram_chat_id: str = Field("0", alias="SQUIRE_TELEGRAM_CHAT_ID")

    # Embedding provider (plan 17-07)
    squire_embedding_provider: str = Field(
        "voyage", alias="SQUIRE_EMBEDDING_PROVIDER"
    )  # voyage | local_bge (local_bge reserved for future offline fallback)
    squire_embedding_model: str = Field(
        "voyage-3-large", alias="SQUIRE_EMBEDDING_MODEL"
    )
    squire_embedding_dim: int = Field(1024, alias="SQUIRE_EMBEDDING_DIM")
    voyage_api_key: SecretStr | None = Field(None, alias="VOYAGE_API_KEY")

    # GRC corpus location (container-internal path at /grc, local at docs/grc)
    squire_grc_dir: str = Field("/grc", alias="SQUIRE_GRC_DIR")

    # Service
    service_port: int = Field(8020, alias="SQUIRE_PORT")
    log_level: str = Field("INFO", alias="SQUIRE_LOG_LEVEL")

    # Keycloak agent IAM (Phase 20 / JIT-CA Gate 2 scaffold).
    # Squire fetches a service-account token via client_credentials. Token use
    # for tool calls is JIT-CA Gate 4 work and is not enforced yet. Setting
    # kc_enabled=False skips Keycloak entirely (safe for environments without
    # the realm provisioned).
    kc_enabled: bool = Field(False, alias="SQUIRE_KC_ENABLED")
    kc_base_url: str = Field("http://cd-service-keycloak:8080", alias="KC_BASE_URL")
    kc_realm: str = Field("coredirective", alias="KC_REALM")
    kc_client_id: str = Field("squire", alias="KC_CLIENT_ID")
    kc_client_secret: SecretStr | None = Field(None, alias="KC_CLIENT_SQUIRE_SECRET")
    kc_token_refresh_skew_seconds: int = Field(10, alias="KC_TOKEN_REFRESH_SKEW_SECONDS")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Lazy proxy so `from .settings import settings` works while also allowing
# env_vars to be present only when a method is called.
class _SettingsProxy:
    def __getattr__(self, name: str):
        return getattr(get_settings(), name)


settings = _SettingsProxy()
