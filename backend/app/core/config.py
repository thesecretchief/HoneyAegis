"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """HoneyAegis configuration loaded from environment variables."""

    # App
    honeyaegis_env: str = "production"
    honeyaegis_debug: bool = False
    honeyaegis_secret_key: str = "change-me-to-a-random-64-char-string"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "honeyaegis"
    postgres_user: str = "honeyaegis"
    postgres_password: str = "change-me-postgres-password"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "change-me-redis-password"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Admin
    admin_email: str = "admin@honeyaegis.local"
    admin_password: str = "changeme"

    # Ollama
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_enabled: bool = False
    ollama_model: str = "phi3:mini"

    # GeoIP
    geoip_db_path: str = "/data/geoip/GeoLite2-City.mmdb"
    maxmind_license_key: str = ""

    # AbuseIPDB
    abuseipdb_api_key: str = ""

    # Alerts (Apprise)
    apprise_urls: str = ""
    alert_on_new_session: bool = True
    alert_on_malware_capture: bool = True
    alert_cooldown_minutes: int = 5

    # SaaS Relay
    relay_enabled: bool = False

    # Stripe Billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Analytics (opt-in)
    analytics_enabled: bool = False

    # Threat Intel Feeds
    otx_api_key: str = ""
    misp_url: str = ""
    misp_api_key: str = ""
    misp_verify_ssl: bool = True
    virustotal_api_key: str = ""

    # Malware Sandbox (Cuckoo/CAPE)
    cuckoo_api_url: str = ""

    # SSO / OIDC
    oidc_enabled: bool = False
    oidc_provider: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_issuer_url: str = ""

    # HA
    flower_user: str = "admin"
    flower_password: str = "change-me-flower-password"

    # Rate Limiting
    rate_limit_global_capacity: int = 100
    rate_limit_global_refill: int = 10
    rate_limit_auth_capacity: int = 10
    rate_limit_auth_refill: int = 1

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    @property
    def cors_origins(self) -> list[str]:
        if self.honeyaegis_debug:
            return ["*"]
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
