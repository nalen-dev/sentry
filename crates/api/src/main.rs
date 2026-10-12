mod auth;
mod error;
mod ingest;
mod public;

use axum::{
    extract::DefaultBodyLimit,
    routing::{get, post, put},
    Router,
};
use chrono::{Duration, Utc};
use sqlx::{postgres::PgPoolOptions, PgPool};
use tower_http::cors::{Any, CorsLayer};

#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool,
}

/// Pastikan partisi riwayat untuk hari ini sampai 3 hari ke depan sudah ada.
async fn ensure_partitions(pool: &PgPool) -> Result<(), sqlx::Error> {
    let today = Utc::now().date_naive();
    for i in 0..=3 {
        sqlx::query("SELECT ensure_history_partition($1)")
            .bind(today + Duration::days(i))
            .execute(pool)
            .await?;
    }
    Ok(())
}

#[tokio::main]
async fn main() {
    let db_url = std::env::var("DATABASE_URL").expect("DATABASE_URL belum diset");
    let pool = PgPoolOptions::new()
        .max_connections(10)
        // Partisi dibatasi per hari UTC, jadi sesi harus UTC.
        .after_connect(|conn, _| {
            Box::pin(async move {
                sqlx::query("SET TIME ZONE 'UTC'").execute(conn).await?;
                Ok(())
            })
        })
        .connect(&db_url)
        .await
        .expect("gagal terhubung ke database");

    sqlx::migrate!("./migrations").run(&pool).await.expect("migrasi gagal");
    ensure_partitions(&pool).await.expect("gagal membuat partisi");

    // Subcommand administrasi: dts-api create-key <site_code> <agent|reader>
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("create-key") {
        let (site, role) = (args.get(2), args.get(3));
        match (site, role) {
            (Some(site), Some(role)) => {
                let key = auth::create_key(&pool, site, role).await.expect("gagal membuat key");
                println!("API key ({role}, site {site}) - simpan sekarang, tidak bisa dilihat lagi:\n{key}");
            }
            _ => eprintln!("pemakaian: dts-api create-key <site_code> <agent|reader>"),
        }
        return;
    }

    // Buat partisi baru tiap jam (murah, idempotent).
    let bg_pool = pool.clone();
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(std::time::Duration::from_secs(3600)).await;
            if let Err(e) = ensure_partitions(&bg_pool).await {
                eprintln!("ensure_partitions gagal: {e}");
            }
        }
    });

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(|| async { "ok" }))
        // Ingestion endpoints (Agent -> Cloud)
        .route("/api/v1/ingest/live", post(ingest::live))
        .route("/api/v1/ingest/history", post(ingest::history))
        .route("/api/v1/ingest/alarm", post(ingest::alarm))
        .route("/api/v1/ingest/segments", put(ingest::segments))
        // Authentication and session endpoints
        .route("/api/v1/auth/login", post(public::login))
        .route("/api/v1/auth/heartbeat", post(public::heartbeat))
        .route("/api/v1/auth/logout", post(public::logout))
        .route("/api/v1/auth/sessions/active", get(public::active_sessions))
        // User management (Pro tier)
        .route("/api/v1/users", get(public::list_users).post(public::create_user))
        // Public REST endpoints
        .route("/api/v1/temperatures/live", get(public::live))
        .route("/api/v1/segments", get(public::segments))
        .route("/api/v1/alarms", get(public::alarms))
        // Web Frontend specific data endpoints
        .route("/api/v1/web/live_segments", get(public::web_live_segments))
        .route("/api/v1/history/groups", get(public::groups_history))
        .route("/api/v1/history/summary", get(public::history_summary))
        .route("/api/v1/history/segment", get(public::segment_history))
        .route("/api/v1/spatial/profile", get(public::spatial_profile))
        .route("/api/v1/logs/system", get(public::system_logs).post(public::write_system_log))
        .route("/api/v1/settings/all", get(public::get_all_settings))
        .layer(DefaultBodyLimit::max(10 * 1024 * 1024))
        .layer(cors)
        .with_state(AppState { pool });

    let addr = std::env::var("BIND_ADDR").unwrap_or_else(|_| "0.0.0.0:8080".into());
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    println!("dts-api listening on {addr}");
    axum::serve(listener, app).await.unwrap();
}
