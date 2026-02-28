-- =============================================================================
-- HoneyAegis Database Schema - Initial Migration
-- =============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Users (dashboard authentication)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    model_used VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Alerts
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
