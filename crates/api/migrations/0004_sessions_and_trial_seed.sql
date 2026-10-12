-- Migration 0004: User sessions tracking and seed TCM-TRIAL account

CREATE TABLE IF NOT EXISTS user_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    session_id TEXT NOT NULL UNIQUE,
    ip_address TEXT,
    user_agent TEXT,
    last_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_session_user_last_seen ON user_session (user_id, last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_user_session_last_seen ON user_session (last_seen DESC);

-- Seed user TCM-TRIAL (password: TCMDTS2026, SHA256: 6e2d7c3775cce935531795d1953c78920c71afc77b3d1227fb4422a31e037bb9)
INSERT INTO app_user (username, password_hash, user_id, role, plan)
VALUES (
    'TCM-TRIAL',
    '6e2d7c3775cce935531795d1953c78920c71afc77b3d1227fb4422a31e037bb9',
    'TCM-001',
    'OPERATOR',
    'trial'
)
ON CONFLICT (username) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    plan = 'trial',
    role = 'OPERATOR';
