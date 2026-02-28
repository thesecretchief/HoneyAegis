-- =============================================================================
-- HoneyAegis Database Schema - Initial Migration
-- =============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Tenants (multi-tenant isolation)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#f59e0b',
    display_name VARCHAR(255),
    portal_domain VARCHAR(255),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default tenant (created on first boot)
INSERT INTO tenants (slug, name, display_name, primary_color)
VALUES ('default', 'Default Organization', 'HoneyAegis', '#f59e0b')
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Users (dashboard authentication)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Sensors (fleet management)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    sensor_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hostname VARCHAR(255),
    ip_address INET,
    status VARCHAR(20) DEFAULT 'active',
    last_seen TIMESTAMPTZ,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Sessions (attacker connections)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    sensor_id UUID REFERENCES sensors(id) ON DELETE SET NULL,
    protocol VARCHAR(20) NOT NULL,
    src_ip INET NOT NULL,
    src_port INTEGER,
    dst_port INTEGER,
    username VARCHAR(255),
    password VARCHAR(255),
    auth_success BOOLEAN DEFAULT false,
    ttylog_file VARCHAR(500),
    duration_seconds FLOAT,
    commands_count INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    country_code VARCHAR(2),
    country_name VARCHAR(100),
    city VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- Convert sessions to a TimescaleDB hypertable for efficient time-series queries
SELECT create_hypertable('sessions', 'started_at', if_not_exists => TRUE);

-- ---------------------------------------------------------------------------
-- Events (individual actions within a session)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    src_ip INET,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('events', 'timestamp', if_not_exists => TRUE);

-- ---------------------------------------------------------------------------
-- Commands (captured attacker commands)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS commands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    output TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    success BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('commands', 'timestamp', if_not_exists => TRUE);

-- ---------------------------------------------------------------------------
-- Downloads (captured malware/files)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS downloads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    url TEXT,
    filename VARCHAR(500),
    file_hash_sha256 VARCHAR(64),
    file_size BIGINT,
    content_type VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- GeoIP Cache
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS geoip_cache (
    ip INET PRIMARY KEY,
    country_code VARCHAR(2),
    country_name VARCHAR(100),
    city VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    asn INTEGER,
    org VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- AI Summaries
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    threat_level VARCHAR(20),
    mitre_ttps JSONB DEFAULT '[]',
    recommendations TEXT,
    model_used VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Alerts
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Honey Tokens (decoy credentials and files)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS honey_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    token_type VARCHAR(50) NOT NULL DEFAULT 'credential',
    name VARCHAR(255) NOT NULL,
    description TEXT,
    username VARCHAR(255),
    password VARCHAR(255),
    filename VARCHAR(500),
    file_path VARCHAR(1000),
    is_active BOOLEAN DEFAULT true,
    trigger_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMPTZ,
    alert_severity VARCHAR(20) DEFAULT 'critical',
    webhook_url VARCHAR(1000),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Webhooks (auto-response hooks)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(1000) NOT NULL,
    secret VARCHAR(255),
    trigger_on VARCHAR(50) NOT NULL DEFAULT 'alert',
    severity_filter VARCHAR(50),
    http_method VARCHAR(10) DEFAULT 'POST',
    headers JSONB DEFAULT '{}',
    payload_template JSONB,
    is_active BOOLEAN DEFAULT true,
    execution_count INTEGER DEFAULT 0,
    last_executed_at TIMESTAMPTZ,
    last_status_code INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sessions_src_ip ON sessions (src_ip);
CREATE INDEX IF NOT EXISTS idx_sessions_protocol ON sessions (protocol);
CREATE INDEX IF NOT EXISTS idx_sessions_sensor_id ON sessions (sensor_id);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON events (session_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_commands_session_id ON commands (session_id);
CREATE INDEX IF NOT EXISTS idx_downloads_session_id ON downloads (session_id);
CREATE INDEX IF NOT EXISTS idx_downloads_file_hash ON downloads (file_hash_sha256);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts (severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts (acknowledged);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_session_id ON ai_summaries (session_id);

-- Tenant isolation indexes
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users (tenant_id);
CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id ON sessions (tenant_id);
CREATE INDEX IF NOT EXISTS idx_sensors_tenant_id ON sensors (tenant_id);
CREATE INDEX IF NOT EXISTS idx_alerts_tenant_id ON alerts (tenant_id);
CREATE INDEX IF NOT EXISTS idx_honey_tokens_tenant_id ON honey_tokens (tenant_id);
CREATE INDEX IF NOT EXISTS idx_honey_tokens_username ON honey_tokens (username);
CREATE INDEX IF NOT EXISTS idx_webhooks_tenant_id ON webhooks (tenant_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_trigger_on ON webhooks (trigger_on);
