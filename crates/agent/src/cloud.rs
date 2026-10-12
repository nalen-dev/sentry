//! Klien HTTP ke cloud + loop pengirim antrean (retry dengan backoff).

use std::{sync::Arc, time::Duration};

use reqwest::{Method, StatusCode};

use crate::outbox::{Outbox, KIND_ALARM, KIND_HISTORY, KIND_SEGMENTS};

pub enum SendError {
    /// Gagal sementara (jaringan, 5xx, 401/403/429): simpan di antrean, coba lagi.
    Retry(String),
    /// Ditolak permanen (payload tidak valid): buang agar tidak memblokir antrean.
    Drop(String),
}

pub struct Cloud {
    client: reqwest::Client,
    base: String,
    api_key: String,
    dry_run: bool,
}

impl Cloud {
    pub fn new(base: String, api_key: String, dry_run: bool) -> Self {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(15))
            .build()
            .expect("gagal membuat HTTP client");
        Self { client, base, api_key, dry_run }
    }

    pub async fn send(&self, method: Method, path: &str, body: String) -> Result<(), SendError> {
        if self.dry_run {
            println!("[dry-run] {method} {path} ({} byte)", body.len());
            return Ok(());
        }
        let res = self
            .client
            .request(method, format!("{}{}", self.base, path))
            .header("X-API-Key", &self.api_key)
            .header("Content-Type", "application/json")
            .body(body)
            .send()
            .await
            .map_err(|e| SendError::Retry(e.to_string()))?;
        let status = res.status();
        if status.is_success() {
            Ok(())
        } else if matches!(status, StatusCode::BAD_REQUEST | StatusCode::PAYLOAD_TOO_LARGE | StatusCode::UNPROCESSABLE_ENTITY) {
            Err(SendError::Drop(format!("HTTP {status}")))
        } else {
            Err(SendError::Retry(format!("HTTP {status}")))
        }
    }
}

fn route(kind: &str) -> (Method, &'static str) {
    match kind {
        KIND_SEGMENTS => (Method::PUT, "/ingest/segments"),
        KIND_ALARM => (Method::POST, "/ingest/alarm"),
        KIND_HISTORY => (Method::POST, "/ingest/history"),
        _ => (Method::POST, "/ingest/unknown"),
    }
}

/// Mengosongkan antrean secara berurutan. Berhenti sementara (backoff) bila cloud tak terjangkau.
pub async fn run_sender(outbox: Outbox, cloud: Arc<Cloud>) {
    let mut backoff = 1u64;
    loop {
        let item = match outbox.next().await {
            Ok(Some(item)) => item,
            Ok(None) => {
                tokio::time::sleep(Duration::from_secs(2)).await;
                continue;
            }
            Err(e) => {
                eprintln!("[outbox] gagal membaca antrean: {e}");
                tokio::time::sleep(Duration::from_secs(5)).await;
                continue;
            }
        };
        let (method, path) = route(&item.kind);
        match cloud.send(method, path, item.payload).await {
            Ok(()) => {
                backoff = 1;
                if let Err(e) = outbox.done(item.id).await {
                    eprintln!("[outbox] gagal menghapus item {}: {e}", item.id);
                }
            }
            Err(SendError::Drop(why)) => {
                eprintln!("[sender] {} #{} dibuang ({why})", item.kind, item.id);
                let _ = outbox.done(item.id).await;
            }
            Err(SendError::Retry(why)) => {
                let pending = outbox.pending().await.unwrap_or(-1);
                eprintln!("[sender] {} gagal ({why}); antrean {pending}, coba lagi {backoff}s", item.kind);
                tokio::time::sleep(Duration::from_secs(backoff)).await;
                backoff = (backoff * 2).min(60);
            }
        }
    }
}
