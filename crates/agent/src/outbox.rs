//! Antrean offline (SQLite) untuk data yang tidak boleh hilang: segmen, alarm, riwayat.
//! Data live tidak diantrekan: hanya snapshot terbaru yang berarti.

use std::path::Path;

use sqlx::{
    sqlite::{SqliteConnectOptions, SqlitePoolOptions},
    SqlitePool,
};

pub const KIND_SEGMENTS: &str = "segments";
pub const KIND_ALARM: &str = "alarm";
pub const KIND_HISTORY: &str = "history";

/// Makin kecil makin didahulukan: segmen (harus ada lebih dulu) -> alarm -> riwayat.
fn priority(kind: &str) -> i32 {
    match kind {
        KIND_SEGMENTS => 0,
        KIND_ALARM => 1,
        _ => 2,
    }
}

/// Batas antrean riwayat (~7 hari bila 1 baris/menit).
const MAX_HISTORY_ITEMS: i64 = 10_080;

pub struct Item {
    pub id: i64,
    pub kind: String,
    pub payload: String,
}

#[derive(Clone)]
pub struct Outbox {
    pool: SqlitePool,
}

impl Outbox {
    pub async fn open(path: &Path) -> Result<Self, sqlx::Error> {
        let opts = SqliteConnectOptions::new().filename(path).create_if_missing(true);
        let pool = SqlitePoolOptions::new().max_connections(2).connect_with(opts).await?;
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                priority INTEGER NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )",
        )
        .execute(&pool)
        .await?;
        // Level alarm terakhir per segmen, agar restart agent tidak memicu TRIGGERED ganda.
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS level_state (
                ch INTEGER NOT NULL, code INTEGER NOT NULL, level INTEGER NOT NULL,
                PRIMARY KEY (ch, code)
            )",
        )
        .execute(&pool)
        .await?;
        Ok(Self { pool })
    }

    pub async fn enqueue(&self, kind: &str, payload: &str) -> Result<(), sqlx::Error> {
        sqlx::query("INSERT INTO outbox (kind, priority, payload) VALUES (?, ?, ?)")
            .bind(kind)
            .bind(priority(kind))
            .bind(payload)
            .execute(&self.pool)
            .await?;
        if kind == KIND_HISTORY {
            // Jaga ukuran: buang riwayat terlama bila internet mati sangat lama.
            sqlx::query(
                "DELETE FROM outbox WHERE kind = ? AND id NOT IN
                 (SELECT id FROM outbox WHERE kind = ? ORDER BY id DESC LIMIT ?)",
            )
            .bind(KIND_HISTORY)
            .bind(KIND_HISTORY)
            .bind(MAX_HISTORY_ITEMS)
            .execute(&self.pool)
            .await?;
        }
        Ok(())
    }

    pub async fn next(&self) -> Result<Option<Item>, sqlx::Error> {
        let row: Option<(i64, String, String)> =
            sqlx::query_as("SELECT id, kind, payload FROM outbox ORDER BY priority, id LIMIT 1")
                .fetch_optional(&self.pool)
                .await?;
        Ok(row.map(|(id, kind, payload)| Item { id, kind, payload }))
    }

    pub async fn done(&self, id: i64) -> Result<(), sqlx::Error> {
        sqlx::query("DELETE FROM outbox WHERE id = ?").bind(id).execute(&self.pool).await?;
        Ok(())
    }

    pub async fn load_levels(&self) -> Result<Vec<(i32, i32, i32)>, sqlx::Error> {
        sqlx::query_as("SELECT ch, code, level FROM level_state").fetch_all(&self.pool).await
    }

    pub async fn save_level(&self, ch: i32, code: i32, level: i32) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO level_state (ch, code, level) VALUES (?, ?, ?)
             ON CONFLICT(ch, code) DO UPDATE SET level = excluded.level",
        )
        .bind(ch)
        .bind(code)
        .bind(level)
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn pending(&self) -> Result<i64, sqlx::Error> {
        let (n,): (i64,) = sqlx::query_as("SELECT COUNT(*) FROM outbox").fetch_one(&self.pool).await?;
        Ok(n)
    }
}
