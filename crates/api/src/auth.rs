use axum::http::HeaderMap;
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use sqlx::{PgPool, Row};

use crate::error::AppError;

pub const JWT_SECRET: &[u8] = b"sentry-dts-super-secret-jwt-key-2026";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,       // user_id e.g. AD-001
    pub username: String,  // username e.g. admin
    pub role: String,      // ADMINISTRATOR / OPERATOR / VIEWER
    #[serde(default = "default_plan")]
    pub plan: String,      // trial / pro
    #[serde(default)]
    pub session_id: Option<String>,
    pub exp: usize,        // expiration timestamp
}

fn default_plan() -> String {
    "trial".to_string()
}

pub struct Principal {
    pub site_id: Option<i16>,
    pub role: String,
}

pub fn hash_key(key: &str) -> String {
    hex::encode(Sha256::digest(key.as_bytes()))
}

pub fn generate_jwt(user_id: &str, username: &str, role: &str, plan: &str, session_id: Option<&str>) -> Result<String, jsonwebtoken::errors::Error> {
    let exp = chrono::Utc::now()
        .checked_add_signed(chrono::Duration::days(7))
        .expect("valid timestamp")
        .timestamp() as usize;

    let claims = Claims {
        sub: user_id.to_string(),
        username: username.to_string(),
        role: role.to_string(),
        plan: plan.to_string(),
        session_id: session_id.map(ToString::to_string),
        exp,
    };

    encode(&Header::default(), &claims, &EncodingKey::from_secret(JWT_SECRET))
}

pub fn verify_jwt(token: &str) -> Result<Claims, AppError> {
    decode::<Claims>(
        token,
        &DecodingKey::from_secret(JWT_SECRET),
        &Validation::default(),
    )
    .map(|data| data.claims)
    .map_err(|_| AppError::unauthorized())
}

pub fn extract_claims_from_headers(headers: &HeaderMap) -> Result<Claims, AppError> {
    if let Some(auth_val) = headers.get("authorization").and_then(|v| v.to_str().ok()) {
        if let Some(token) = auth_val.strip_prefix("Bearer ") {
            return verify_jwt(token);
        }
    }
    Err(AppError::unauthorized())
}

/// Verifikasi header X-API-Key untuk role tertentu (mis. "agent").
pub async fn authenticate(pool: &PgPool, headers: &HeaderMap, role: &str) -> Result<Principal, AppError> {
    let key = headers.get("x-api-key").and_then(|v| v.to_str().ok()).ok_or_else(AppError::unauthorized)?;
    let row = sqlx::query("SELECT site_id, role FROM api_key WHERE key_hash = $1 AND NOT revoked")
        .bind(hash_key(key))
        .fetch_optional(pool)
        .await?
        .ok_or_else(AppError::unauthorized)?;
    let p = Principal { site_id: row.get("site_id"), role: row.get("role") };
    if p.role != role {
        return Err(AppError::forbidden());
    }
    Ok(p)
}

/// Verifikasi akses pembaca: boleh dari X-API-Key (role reader) ATAU Authorization: Bearer <JWT>
pub async fn authenticate_reader(pool: &PgPool, headers: &HeaderMap) -> Result<Principal, AppError> {
    // 1. Cek X-API-Key
    if let Some(key) = headers.get("x-api-key").and_then(|v| v.to_str().ok()) {
        let row = sqlx::query("SELECT site_id, role FROM api_key WHERE key_hash = $1 AND NOT revoked")
            .bind(hash_key(key))
            .fetch_optional(pool)
            .await?;
        if let Some(r) = row {
            let role: String = r.get("role");
            if role == "reader" {
                return Ok(Principal { site_id: r.get("site_id"), role });
            }
        }
    }

    // 2. Cek Authorization: Bearer <JWT>
    if let Some(auth_val) = headers.get("authorization").and_then(|v| v.to_str().ok()) {
        if let Some(token) = auth_val.strip_prefix("Bearer ") {
            let claims = verify_jwt(token)?;
            return Ok(Principal {
                site_id: None,
                role: claims.role,
            });
        }
    }

    Err(AppError::unauthorized())
}

/// Buat API key baru (site dibuat otomatis jika belum ada). Hanya hash yang disimpan.
pub async fn create_key(pool: &PgPool, site_code: &str, role: &str) -> Result<String, sqlx::Error> {
    let site_id: i16 = sqlx::query(
        "INSERT INTO site (code, name) VALUES ($1, $1)
         ON CONFLICT (code) DO UPDATE SET code = EXCLUDED.code RETURNING id",
    )
    .bind(site_code)
    .fetch_one(pool)
    .await?
    .get("id");
    let key = format!("dts_{}{}", uuid::Uuid::new_v4().simple(), uuid::Uuid::new_v4().simple());
    // Key pembaca (reader) tidak terikat site.
    let bound_site = if role == "agent" { Some(site_id) } else { None };
    sqlx::query("INSERT INTO api_key (site_id, role, key_hash, label) VALUES ($1, $2, $3, $4)")
        .bind(bound_site)
        .bind(role)
        .bind(hash_key(&key))
        .bind(site_code)
        .execute(pool)
        .await?;
    Ok(key)
}
