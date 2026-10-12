-- Skema cloud DTS (PostgreSQL biasa, tanpa ekstensi).
-- Suhu disimpan dalam derajat Celsius (agent mengonversi dari satuan 0,1 C milik DTS).
-- Acknowledge HANYA dilakukan di lokal; cloud hanya menerima statusnya (read-only).

CREATE TABLE site (
    id          SMALLSERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    last_seen   TIMESTAMPTZ            -- heartbeat agent; dasar status "Site Offline"
);

CREATE TABLE api_key (
    id          SERIAL PRIMARY KEY,
    site_id     SMALLINT REFERENCES site(id),   -- NULL = key pembaca (REST publik)
    role        TEXT NOT NULL CHECK (role IN ('agent', 'reader')),
    key_hash    TEXT NOT NULL UNIQUE,           -- simpan hash, bukan key asli
    label       TEXT,
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Master segmen (hasil sinkronisasi dari opt_fq_list + mapping lokal).
CREATE TABLE segment (
    id             SERIAL PRIMARY KEY,
    site_id        SMALLINT NOT NULL REFERENCES site(id),
    dts_ch         INT NOT NULL,
    dts_code       INT NOT NULL,
    original_name  TEXT NOT NULL,
    custom_name    TEXT,
    main_group     TEXT NOT NULL,
    sub_group      TEXT,
    start_m        INT,
    end_m          INT,
    UNIQUE (site_id, dts_ch, dts_code)
);

CREATE TABLE site_setting (
    site_id  SMALLINT NOT NULL REFERENCES site(id),
    key      TEXT NOT NULL,              -- mis. warning_threshold, critical_threshold
    value    TEXT NOT NULL,
    PRIMARY KEY (site_id, key)
);

-- Kondisi terkini: di-UPSERT, ukurannya tetap kecil.
CREATE TABLE live_segment (
    segment_id   INT PRIMARY KEY REFERENCES segment(id),
    temp_avg     REAL NOT NULL,
    temp_min     REAL NOT NULL,
    temp_max     REAL NOT NULL,
    temp_min_p   INT,
    temp_max_p   INT,
    status       TEXT NOT NULL CHECK (status IN ('NORMAL', 'WARNING', 'CRITICAL')),
    measured_at  TIMESTAMPTZ NOT NULL
);

-- Profil spasial terkini per titik sensor (hanya yang terbaru, tanpa riwayat).
CREATE TABLE live_point (
    site_id      SMALLINT NOT NULL REFERENCES site(id),
    dts_ch       INT NOT NULL,
    dts_code     INT NOT NULL,
    temp         REAL,                   -- NULL = tidak ada sensor (-2731 di DTS)
    measured_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (site_id, dts_ch, dts_code)
);

-- Riwayat agregat 1 menit, dipartisi per hari. Retention: DROP PARTITION (14 hari).
CREATE TABLE segment_history_1m (
    segment_id  INT NOT NULL,
    ts          TIMESTAMPTZ NOT NULL,    -- awal menit
    temp_avg    REAL NOT NULL,
    temp_min    REAL NOT NULL,
    temp_max    REAL NOT NULL,
    PRIMARY KEY (segment_id, ts)
) PARTITION BY RANGE (ts);

-- Riwayat agregat 1 jam, disimpan selamanya (diisi dari 1m sebelum partisi dibuang).
CREATE TABLE segment_history_1h (
    segment_id  INT NOT NULL REFERENCES segment(id),
    ts          TIMESTAMPTZ NOT NULL,
    temp_avg    REAL NOT NULL,
    temp_min    REAL NOT NULL,
    temp_max    REAL NOT NULL,
    PRIMARY KEY (segment_id, ts)
);

-- Event alarm dari agent. event_id dibuat di site -> kiriman ulang aman (idempotent).
CREATE TABLE alarm_event (
    id           BIGSERIAL PRIMARY KEY,
    site_id      SMALLINT NOT NULL REFERENCES site(id),
    event_id     UUID NOT NULL,
    segment_id   INT NOT NULL REFERENCES segment(id),
    event_type   TEXT NOT NULL CHECK (event_type IN ('TRIGGERED', 'CLEARED', 'ACKNOWLEDGED')),
    level        TEXT CHECK (level IN ('WARNING', 'CRITICAL')),
    temperature  REAL,
    threshold    REAL,
    occurred_at  TIMESTAMPTZ NOT NULL,
    received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (site_id, event_id)
);
CREATE INDEX alarm_event_time_idx ON alarm_event (occurred_at DESC);

-- Membuat partisi harian. Dipanggil oleh API saat start dan tiap hari.
CREATE FUNCTION ensure_history_partition(d DATE) RETURNS VOID AS $$
DECLARE
    pname TEXT := format($f$segment_history_1m_%s$f$, to_char(d, $f$YYYYMMDD$f$));
BEGIN
    EXECUTE format(
        $f$CREATE TABLE IF NOT EXISTS %I PARTITION OF segment_history_1m
           FOR VALUES FROM (%L) TO (%L)$f$,
        pname, d, d + 1);
END;
$$ LANGUAGE plpgsql;
