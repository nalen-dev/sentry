//! Konfigurasi agent dari environment variable.
//!
//! DTS_CLOUD_URL            mis. https://dts.example.com/api/v1      (wajib kecuali dry-run)
//! DTS_API_KEY              API key role agent                        (wajib kecuali dry-run)
//! DTS_SQLITE_PATH          sentry_scada.db milik aplikasi desktop (default: folder data app)
//! DTS_QUEUE_PATH           file antrean offline (default: agent_queue.db di folder yang sama)
//! DTS_LIVE_INTERVAL_SECS   interval snapshot live (default 10)
//! DTS_DRY_RUN=1            tidak mengirim, hanya mencetak ringkasan
//! DTS_MYSQL_HOST/PORT/USER/PASS/NAME   menimpa pengaturan db_* dari sentry_scada.db

use std::{path::PathBuf, time::Duration};

#[derive(Default, Clone)]
pub struct MysqlOverride {
    pub host: Option<String>,
    pub port: Option<String>,
    pub user: Option<String>,
    pub pass: Option<String>,
    pub name: Option<String>,
}

pub struct Config {
    pub sqlite_path: PathBuf,
    pub queue_path: PathBuf,
    pub cloud_url: String,
    pub api_key: String,
    pub live_interval: Duration,
    pub dry_run: bool,
    pub mysql: MysqlOverride,
}

fn env(key: &str) -> Option<String> {
    std::env::var(key).ok().filter(|v| !v.is_empty())
}

fn default_data_dir() -> PathBuf {
    if let Some(local) = env("LOCALAPPDATA") {
        PathBuf::from(local).join("com.sentry.app")
    } else if let Some(home) = env("HOME") {
        PathBuf::from(home).join(".local/share/com.sentry.app")
    } else {
        PathBuf::from(".")
    }
}

impl Config {
    pub fn from_env() -> Result<Self, String> {
        let dry_run = env("DTS_DRY_RUN").is_some_and(|v| v == "1" || v.eq_ignore_ascii_case("true"));
        let cloud_url = env("DTS_CLOUD_URL").unwrap_or_default();
        let api_key = env("DTS_API_KEY").unwrap_or_default();
        if !dry_run && (cloud_url.is_empty() || api_key.is_empty()) {
            return Err("DTS_CLOUD_URL dan DTS_API_KEY wajib diisi (atau set DTS_DRY_RUN=1)".into());
        }
        let dir = default_data_dir();
        let secs = env("DTS_LIVE_INTERVAL_SECS").and_then(|v| v.parse().ok()).unwrap_or(10u64).max(1);
        Ok(Self {
            sqlite_path: env("DTS_SQLITE_PATH").map(PathBuf::from).unwrap_or_else(|| dir.join("sentry_scada.db")),
            queue_path: env("DTS_QUEUE_PATH").map(PathBuf::from).unwrap_or_else(|| dir.join("agent_queue.db")),
            cloud_url: cloud_url.trim_end_matches('/').to_string(),
            api_key,
            live_interval: Duration::from_secs(secs),
            dry_run,
            mysql: MysqlOverride {
                host: env("DTS_MYSQL_HOST"),
                port: env("DTS_MYSQL_PORT"),
                user: env("DTS_MYSQL_USER"),
                pass: env("DTS_MYSQL_PASS"),
                name: env("DTS_MYSQL_NAME"),
            },
        })
    }
}
