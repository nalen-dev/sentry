-- Migration 0002: Web users and system logs

CREATE TABLE app_user (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    user_id       TEXT NOT NULL UNIQUE, -- e.g. AD-001, OP-7729
    role          TEXT NOT NULL CHECK (role IN ('ADMINISTRATOR', 'OPERATOR', 'VIEWER')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE system_log (
    id          BIGSERIAL PRIMARY KEY,
    site_id     SMALLINT REFERENCES site(id),
    event_type  TEXT NOT NULL,
    message     TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX system_log_time_idx ON system_log (occurred_at DESC);

-- Default users for web login
-- Passwords:
-- admin: admin123
-- operator: operator123
-- viewer: viewer123
-- Using SHA256 hashes as a simple standard for internal industrial SCADA:
-- admin123 -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- operator123 -> a0988089ae1925b6a7a51bbbbcdba0d9be4cb178652c423ba6ecb8b0e457f6b8
-- viewer123 -> 217a9448ec8df80afecbc1b092cecfcc4213cc12a67a992bc4a8c3d91cf9cc08

INSERT INTO app_user (username, password_hash, user_id, role)
VALUES 
  ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'AD-001', 'ADMINISTRATOR'),
  ('operator', 'a0988089ae1925b6a7a51bbbbcdba0d9be4cb178652c423ba6ecb8b0e457f6b8', 'OP-7729', 'OPERATOR')
ON CONFLICT (username) DO NOTHING;
