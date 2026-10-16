use axum::{
    extract::{Query, State},
    http::HeaderMap,
    Json,
};
use chrono::{DateTime, Utc};
use dts_shared::{ApiResponse, LiveTemperature, SegmentStatus};
use serde::{Deserialize, Serialize};
use sqlx::Row;

use crate::{
    auth::{authenticate_reader, extract_claims_from_headers, generate_jwt, hash_key},
    error::AppError,
    AppState,
};

#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize)]
pub struct LoginResponse {
    pub token: String,
    pub user_id: String,
    pub username: String,
    pub role: String,
    pub plan: String,
}

#[derive(Debug, Serialize)]
pub struct SessionUserItem {
    pub session_id: String,
    pub user_id: String,
    pub username: String,
    pub role: String,
    pub plan: String,
    pub ip_address: Option<String>,
    pub user_agent: Option<String>,
    pub last_seen: DateTime<Utc>,
    pub is_current: bool,
}

#[derive(Debug, Serialize)]
#[serde(tag = "type")]
pub enum ActiveSessionInfo {
    #[serde(rename = "trial")]
    Trial {
        plan: String,
        concurrent_count: i64,
        max_allowed: i64,
    },
    #[serde(rename = "pro")]
    Pro {
        plan: String,
        total_online: usize,
        sessions: Vec<SessionUserItem>,
    },
}

#[derive(Debug, Serialize)]
pub struct AppUserItem {
    pub id: i32,
    pub username: String,
    pub user_id: String,
    pub role: String,
    pub plan: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub username: String,
    pub password: String,
    pub user_id: Option<String>,
    pub role: Option<String>,
    pub plan: Option<String>,
}

/// POST /api/v1/auth/login
pub async fn login(
    State(st): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<LoginRequest>,
) -> Result<Json<ApiResponse<LoginResponse>>, AppError> {
    let pw_hash = hash_key(&body.password);
    let row = sqlx::query("SELECT user_id, username, role, plan FROM app_user WHERE username = $1 AND password_hash = $2")
        .bind(&body.username)
        .bind(&pw_hash)
        .fetch_optional(&st.pool)
        .await?;

    let row = match row {
        Some(r) => r,
        None => return Err(AppError(axum::http::StatusCode::UNAUTHORIZED, "Invalid username or password.".into())),
    };

    let user_id: String = row.get("user_id");
    let username: String = row.get("username");
    let role: String = row.get("role");
    let plan: String = row.get("plan");

    // If trial plan: enforce max 10 concurrent active sessions
    if plan == "trial" {
        let active_count: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM user_session WHERE user_id = $1 AND last_seen > now() - INTERVAL '15 minutes'"
        )
        .bind(&user_id)
        .fetch_one(&st.pool)
        .await?;

        if active_count >= 10 {
            return Err(AppError(
                axum::http::StatusCode::FORBIDDEN,
                "Concurrent device quota exceeded. Trial tier is limited to 10 concurrent active devices. Please close other active browser sessions or contact KAG for Enterprise Pro.".into(),
            ));
        }
    }

    let session_id = uuid::Uuid::new_v4().to_string();
    let ip_address = headers
        .get("x-forwarded-for")
        .and_then(|v| v.to_str().ok())
        .map(|s| s.split(',').next().unwrap_or(s).trim().to_string())
        .or_else(|| {
            headers
                .get("x-real-ip")
                .and_then(|v| v.to_str().ok())
                .map(ToString::to_string)
        });

    let user_agent = headers
        .get("user-agent")
        .and_then(|v| v.to_str().ok())
        .map(ToString::to_string);

    sqlx::query(
        "INSERT INTO user_session (user_id, session_id, ip_address, user_agent, last_seen)
         VALUES ($1, $2, $3, $4, now())"
    )
    .bind(&user_id)
    .bind(&session_id)
    .bind(&ip_address)
    .bind(&user_agent)
    .execute(&st.pool)
    .await?;

    let token = generate_jwt(&user_id, &username, &role, &plan, Some(&session_id))
        .map_err(|_| AppError(axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Failed to generate access token.".into()))?;

    Ok(Json(ApiResponse::ok(
        "Login successful",
        LoginResponse {
            token,
            user_id,
            username,
            role,
            plan,
        },
    )))
}

/// POST /api/v1/auth/heartbeat
pub async fn heartbeat(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<serde_json::Value>>, AppError> {
    let claims = extract_claims_from_headers(&headers)?;
    if let Some(session_id) = &claims.session_id {
        sqlx::query("UPDATE user_session SET last_seen = now() WHERE session_id = $1")
            .bind(session_id)
            .execute(&st.pool)
            .await?;
    }
    Ok(Json(ApiResponse::ok("Heartbeat ok", serde_json::json!({ "status": "active" }))))
}

/// POST /api/v1/auth/logout
pub async fn logout(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<serde_json::Value>>, AppError> {
    if let Ok(claims) = extract_claims_from_headers(&headers) {
        if let Some(session_id) = &claims.session_id {
            let _ = sqlx::query("DELETE FROM user_session WHERE session_id = $1")
                .bind(session_id)
                .execute(&st.pool)
                .await;
        }
    }
    Ok(Json(ApiResponse::ok("Logout successful", serde_json::json!({}))))
}

/// GET /api/v1/auth/sessions/active
pub async fn active_sessions(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<ActiveSessionInfo>>, AppError> {
    let claims = extract_claims_from_headers(&headers)?;

    if claims.plan == "trial" {
        let count: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM user_session WHERE user_id = $1 AND last_seen > now() - INTERVAL '15 minutes'"
        )
        .bind(&claims.sub)
        .fetch_one(&st.pool)
        .await?;

        Ok(Json(ApiResponse::ok(
            "Active session summary",
            ActiveSessionInfo::Trial {
                plan: "trial".into(),
                concurrent_count: count.max(1),
                max_allowed: 10,
            },
        )))
    } else {
        let rows = sqlx::query(
            "SELECT s.session_id, s.user_id, u.username, u.role, u.plan, s.ip_address, s.user_agent, s.last_seen
             FROM user_session s
             JOIN app_user u ON u.user_id = s.user_id
             WHERE s.last_seen > now() - INTERVAL '15 minutes'
             ORDER BY s.last_seen DESC"
        )
        .fetch_all(&st.pool)
        .await?;

        let sessions = rows
            .into_iter()
            .map(|r| {
                let sid: String = r.get("session_id");
                let is_current = claims.session_id.as_deref() == Some(&sid);
                SessionUserItem {
                    session_id: sid,
                    user_id: r.get("user_id"),
                    username: r.get("username"),
                    role: r.get("role"),
                    plan: r.get("plan"),
                    ip_address: r.get("ip_address"),
                    user_agent: r.get("user_agent"),
                    last_seen: r.get("last_seen"),
                    is_current,
                }
            })
            .collect::<Vec<_>>();

        let total = sessions.len();
        Ok(Json(ApiResponse::ok(
            "Online users presence",
            ActiveSessionInfo::Pro {
                plan: "pro".into(),
                total_online: total,
                sessions,
            },
        )))
    }
}

/// GET /api/v1/users
pub async fn list_users(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<Vec<AppUserItem>>>, AppError> {
    let claims = extract_claims_from_headers(&headers)?;
    if claims.plan != "pro" && claims.role != "ADMINISTRATOR" {
        return Err(AppError(
            axum::http::StatusCode::FORBIDDEN,
            "User management is reserved for Enterprise Pro accounts.".into(),
        ));
    }

    let rows = sqlx::query(
        "SELECT id, username, user_id, role, plan, created_at FROM app_user ORDER BY created_at ASC"
    )
    .fetch_all(&st.pool)
    .await?;

    let users = rows
        .into_iter()
        .map(|r| AppUserItem {
            id: r.get("id"),
            username: r.get("username"),
            user_id: r.get("user_id"),
            role: r.get("role"),
            plan: r.get("plan"),
            created_at: r.get("created_at"),
        })
        .collect();

    Ok(Json(ApiResponse::ok("Users retrieved", users)))
}

/// POST /api/v1/users
pub async fn create_user(
    State(st): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<CreateUserRequest>,
) -> Result<Json<ApiResponse<AppUserItem>>, AppError> {
    let claims = extract_claims_from_headers(&headers)?;
    if claims.plan != "pro" && claims.role != "ADMINISTRATOR" {
        return Err(AppError(
            axum::http::StatusCode::FORBIDDEN,
            "User provisioning is reserved for Enterprise Pro accounts.".into(),
        ));
    }

    let username = body.username.trim();
    if username.is_empty() || body.password.trim().is_empty() {
        return Err(AppError(
            axum::http::StatusCode::BAD_REQUEST,
            "Username and password cannot be empty.".into(),
        ));
    }

    let role = body.role.as_deref().unwrap_or("OPERATOR").to_uppercase();
    if role != "ADMINISTRATOR" && role != "OPERATOR" && role != "VIEWER" {
        return Err(AppError(
            axum::http::StatusCode::BAD_REQUEST,
            "Invalid role. Must be ADMINISTRATOR, OPERATOR, or VIEWER.".into(),
        ));
    }

    let plan = body.plan.as_deref().unwrap_or("pro").to_lowercase();
    if plan != "trial" && plan != "pro" {
        return Err(AppError(
            axum::http::StatusCode::BAD_REQUEST,
            "Invalid plan. Must be 'trial' or 'pro'.".into(),
        ));
    }

    let user_id = body.user_id.unwrap_or_else(|| {
        let rand_part = &uuid::Uuid::new_v4().simple().to_string()[..6];
        format!("{}-{}", match role.as_str() {
            "ADMINISTRATOR" => "AD",
            "VIEWER" => "VW",
            _ => "OP",
        }, rand_part.to_uppercase())
    });

    let pw_hash = hash_key(&body.password);

    let row = sqlx::query(
        "INSERT INTO app_user (username, password_hash, user_id, role, plan)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id, username, user_id, role, plan, created_at"
    )
    .bind(username)
    .bind(&pw_hash)
    .bind(&user_id)
    .bind(&role)
    .bind(&plan)
    .fetch_one(&st.pool)
    .await
    .map_err(|e| {
        if let Some(db_err) = e.as_database_error() {
            if db_err.is_unique_violation() {
                return AppError(
                    axum::http::StatusCode::CONFLICT,
                    "Username or User ID already exists.".into(),
                );
            }
        }
        AppError::from(e)
    })?;

    let created = AppUserItem {
        id: row.get("id"),
        username: row.get("username"),
        user_id: row.get("user_id"),
        role: row.get("role"),
        plan: row.get("plan"),
        created_at: row.get("created_at"),
    };

    Ok(Json(ApiResponse::ok("User created successfully", created)))
}

/// GET /api/v1/temperatures/live (REST format ringkas)
pub async fn live(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<Vec<LiveTemperature>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = sqlx::query(
        "SELECT COALESCE(s.custom_name, s.original_name) AS name, s.main_group, s.start_m,
                l.temp_max, l.status, l.measured_at
         FROM live_segment l JOIN segment s ON s.id = l.segment_id
         ORDER BY s.main_group, s.dts_ch, s.dts_code",
    )
    .fetch_all(&st.pool)
    .await?;

    let data = rows
        .into_iter()
        .map(|r| {
            let status: String = r.get("status");
            let start_m: Option<i32> = r.get("start_m");
            LiveTemperature {
                segment_code: r.get("name"),
                main_group: r.get("main_group"),
                distance_m: start_m.map(f64::from),
                temperature: r.get("temp_max"),
                status: serde_json::from_value(serde_json::Value::String(status))
                    .unwrap_or(SegmentStatus::Normal),
                last_updated: r.get::<DateTime<Utc>, _>("measured_at"),
            }
        })
        .collect();
    Ok(Json(ApiResponse::ok("Live temperatures retrieved successfully", data)))
}

#[derive(Debug, Serialize)]
pub struct WebLiveSegment {
    pub id: i32,
    pub dts_ch: i32,
    pub dts_code: i32,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
    pub temp_avg: f32,
    pub temp_min: f32,
    pub temp_max: f32,
    pub temp_min_p: i32,
    pub temp_max_p: i32,
}

/// GET /api/v1/web/live_segments (Kompatibel 100% dengan get_live_segments desktop)
pub async fn web_live_segments(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<Vec<WebLiveSegment>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = sqlx::query(
        "SELECT s.id, s.dts_ch, s.dts_code, s.original_name, s.custom_name, s.main_group, s.sub_group,
                s.start_m, s.end_m, l.temp_avg, l.temp_min, l.temp_max,
                COALESCE(l.temp_min_p, 0) as temp_min_p, COALESCE(l.temp_max_p, 0) as temp_max_p
         FROM segment s
         JOIN live_segment l ON s.id = l.segment_id
         ORDER BY s.dts_ch, s.dts_code",
    )
    .fetch_all(&st.pool)
    .await?;

    let data = rows
        .into_iter()
        .map(|r| WebLiveSegment {
            id: r.get("id"),
            dts_ch: r.get("dts_ch"),
            dts_code: r.get("dts_code"),
            original_name: r.get("original_name"),
            custom_name: r.get("custom_name"),
            main_group: r.get("main_group"),
            sub_group: r.get("sub_group"),
            start_m: r.get("start_m"),
            end_m: r.get("end_m"),
            temp_avg: r.get("temp_avg"),
            temp_min: r.get("temp_min"),
            temp_max: r.get("temp_max"),
            temp_min_p: r.get("temp_min_p"),
            temp_max_p: r.get("temp_max_p"),
        })
        .collect();

    Ok(Json(ApiResponse::ok("Live segments retrieved", data)))
}

#[derive(Debug, Serialize)]
pub struct WebSegmentMapping {
    pub id: i32,
    pub dts_ch: i32,
    pub dts_code: i32,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
}

/// GET /api/v1/segments (Kompatibel dengan get_segment_mappings desktop)
pub async fn segments(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<Vec<WebSegmentMapping>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = sqlx::query(
        "SELECT id, dts_ch, dts_code, original_name, custom_name, main_group, sub_group, start_m, end_m
         FROM segment ORDER BY dts_ch, dts_code",
    )
    .fetch_all(&st.pool)
    .await?;

    let data = rows
        .into_iter()
        .map(|r| WebSegmentMapping {
            id: r.get("id"),
            dts_ch: r.get("dts_ch"),
            dts_code: r.get("dts_code"),
            original_name: r.get("original_name"),
            custom_name: r.get("custom_name"),
            main_group: r.get("main_group"),
            sub_group: r.get("sub_group"),
            start_m: r.get("start_m"),
            end_m: r.get("end_m"),
        })
        .collect();

    Ok(Json(ApiResponse::ok("Segments retrieved", data)))
}

#[derive(Debug, Serialize)]
pub struct WebAlarmLog {
    pub id: i64,
    pub time: String,
    pub ch: i32,
    pub code: i32,
    pub distance: i32,
    pub alarm_type: i32,
    pub temp: f32,
    pub is_active: bool,
}

#[derive(Debug, Deserialize)]
pub struct AlarmsQuery {
    pub date: Option<String>,
}

/// GET /api/v1/alarms (Kompatibel dengan get_alarms desktop)
pub async fn alarms(
    State(st): State<AppState>,
    headers: HeaderMap,
    Query(q): Query<AlarmsQuery>,
) -> Result<Json<ApiResponse<Vec<WebAlarmLog>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = if let Some(ref d) = q.date {
        sqlx::query(
            "SELECT a.id, a.occurred_at, s.dts_ch, s.dts_code, COALESCE(s.start_m, 0) as distance,
                    CASE WHEN a.level = 'CRITICAL' THEN 2 ELSE 1 END as alarm_type,
                    COALESCE(a.temperature, 0.0) as temp,
                    (a.event_type = 'TRIGGERED') as is_active
             FROM alarm_event a
             JOIN segment s ON s.id = a.segment_id
             WHERE a.occurred_at::date = $1::date
             ORDER BY a.occurred_at DESC LIMIT 1000",
        )
        .bind(d)
        .fetch_all(&st.pool)
        .await?
    } else {
        sqlx::query(
            "SELECT a.id, a.occurred_at, s.dts_ch, s.dts_code, COALESCE(s.start_m, 0) as distance,
                    CASE WHEN a.level = 'CRITICAL' THEN 2 ELSE 1 END as alarm_type,
                    COALESCE(a.temperature, 0.0) as temp,
                    (a.event_type = 'TRIGGERED') as is_active
             FROM alarm_event a
             JOIN segment s ON s.id = a.segment_id
             ORDER BY a.occurred_at DESC LIMIT 100",
        )
        .fetch_all(&st.pool)
        .await?
    };

    let data = rows
        .into_iter()
        .map(|r| {
            let dt: DateTime<Utc> = r.get("occurred_at");
            WebAlarmLog {
                id: r.get("id"),
                time: dt.to_rfc3339(),
                ch: r.get("dts_ch"),
                code: r.get("dts_code"),
                distance: r.get("distance"),
                alarm_type: r.get("alarm_type"),
                temp: r.get("temp"),
                is_active: r.get("is_active"),
            }
        })
        .collect();

    Ok(Json(ApiResponse::ok("Alarms retrieved", data)))
}

#[derive(Debug, Deserialize)]
pub struct GroupHistoryQuery {
    pub start_dt: Option<String>,
    pub end_dt: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct WebGroupHistoryPoint {
    pub time: String,
    pub groups: std::collections::HashMap<String, f32>,
}

/// GET /api/v1/history/groups (Kompatibel dengan get_groups_history desktop)
pub async fn groups_history(
    State(st): State<AppState>,
    headers: HeaderMap,
    Query(q): Query<GroupHistoryQuery>,
) -> Result<Json<ApiResponse<Vec<WebGroupHistoryPoint>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let start_dt = q.start_dt.unwrap_or_else(|| {
        (Utc::now() - chrono::Duration::hours(24)).to_rfc3339()
    });
    let end_dt = q.end_dt.unwrap_or_else(|| Utc::now().to_rfc3339());

    let rows = sqlx::query(
        "SELECT h.ts, s.main_group, MAX(h.temp_max) as max_temp
         FROM segment_history_1m h
         JOIN segment s ON s.id = h.segment_id
         WHERE s.main_group != 'Unassigned'
           AND h.ts >= $1::timestamptz AND h.ts <= $2::timestamptz
         GROUP BY h.ts, s.main_group
         ORDER BY h.ts ASC",
    )
    .bind(start_dt)
    .bind(end_dt)
    .fetch_all(&st.pool)
    .await?;

    let mut map: std::collections::BTreeMap<String, std::collections::HashMap<String, f32>> =
        std::collections::BTreeMap::new();

    for r in rows {
        let ts: DateTime<Utc> = r.get("ts");
        let time_str = ts.to_rfc3339();
        let group: String = r.get("main_group");
        let temp: f32 = r.get("max_temp");
        map.entry(time_str).or_default().insert(group, temp);
    }

    let data = map
        .into_iter()
        .map(|(time, groups)| WebGroupHistoryPoint { time, groups })
        .collect();

    Ok(Json(ApiResponse::ok("Group history retrieved", data)))
}

#[derive(Debug, Deserialize)]
pub struct SpatialQuery {
    pub main_group: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct WebCurvePoint {
    pub distance: i32,
    pub temp: f32,
}

/// GET /api/v1/spatial/profile (Kompatibel dengan get_spatial_profile desktop)
pub async fn spatial_profile(
    State(st): State<AppState>,
    headers: HeaderMap,
    Query(q): Query<SpatialQuery>,
) -> Result<Json<ApiResponse<Vec<WebCurvePoint>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let group = q.main_group.unwrap_or_else(|| "All".to_string());

    let bound_row = if group == "All" {
        sqlx::query(
            "SELECT dts_ch, MIN(start_m) as min_start, MAX(end_m) as max_end
             FROM segment WHERE start_m IS NOT NULL AND end_m IS NOT NULL
             GROUP BY dts_ch LIMIT 1",
        )
        .fetch_optional(&st.pool)
        .await?
    } else {
        sqlx::query(
            "SELECT dts_ch, MIN(start_m) as min_start, MAX(end_m) as max_end
             FROM segment WHERE main_group = $1 AND start_m IS NOT NULL AND end_m IS NOT NULL
             GROUP BY dts_ch LIMIT 1",
        )
        .bind(&group)
        .fetch_optional(&st.pool)
        .await?
    };

    let bound = match bound_row {
        Some(b) => b,
        None => return Ok(Json(ApiResponse::ok("Empty", vec![]))),
    };

    let ch: i32 = bound.get("dts_ch");
    let min_s: i32 = bound.get("min_start");
    let max_e: i32 = bound.get("max_end");

    let rows = sqlx::query(
        "SELECT dts_code, temp FROM live_point
         WHERE dts_ch = $1 AND dts_code >= $2 AND dts_code <= $3 AND temp IS NOT NULL
         ORDER BY dts_code ASC",
    )
    .bind(ch)
    .bind(min_s)
    .bind(max_e)
    .fetch_all(&st.pool)
    .await?;

    let points = rows
        .into_iter()
        .map(|r| WebCurvePoint {
            distance: r.get("dts_code"),
            temp: r.get("temp"),
        })
        .collect();

    Ok(Json(ApiResponse::ok("Spatial profile retrieved", points)))
}

#[derive(Debug, Serialize)]
pub struct WebHistorySummary {
    pub max_temp: f32,
    pub min_temp: f32,
    pub max_group: String,
    pub max_time: String,
}

/// GET /api/v1/history/summary (Kompatibel dengan get_history_summary desktop)
pub async fn history_summary(
    State(st): State<AppState>,
    headers: HeaderMap,
    Query(q): Query<GroupHistoryQuery>,
) -> Result<Json<ApiResponse<Option<WebHistorySummary>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let start_dt = q.start_dt.unwrap_or_else(|| {
        (Utc::now() - chrono::Duration::hours(24)).to_rfc3339()
    });
    let end_dt = q.end_dt.unwrap_or_else(|| Utc::now().to_rfc3339());

    let row = sqlx::query(
        "SELECT s.main_group, h.ts, h.temp_max, h.temp_min
         FROM segment_history_1m h
         JOIN segment s ON s.id = h.segment_id
         WHERE s.main_group != 'Unassigned'
           AND h.ts >= $1::timestamptz AND h.ts <= $2::timestamptz
         ORDER BY h.temp_max DESC LIMIT 1",
    )
    .bind(start_dt)
    .bind(end_dt)
    .fetch_optional(&st.pool)
    .await?;

    let summary = row.map(|r| {
        let ts: DateTime<Utc> = r.get("ts");
        WebHistorySummary {
            max_temp: r.get("temp_max"),
            min_temp: r.get("temp_min"),
            max_group: r.get("main_group"),
            max_time: ts.to_rfc3339(),
        }
    });

    Ok(Json(ApiResponse::ok("Summary retrieved", summary)))
}

#[derive(Debug, Deserialize)]
pub struct SegmentHistoryQuery {
    pub dts_ch: i32,
    pub dts_code: i32,
    pub minutes: Option<i64>,
}

#[derive(Debug, Serialize)]
pub struct WebSegmentHistoryPoint {
    pub time: String,
    pub temp: f32,
}

/// GET /api/v1/history/segment (Kompatibel dengan get_segment_history desktop)
pub async fn segment_history(
    State(st): State<AppState>,
    headers: HeaderMap,
    Query(q): Query<SegmentHistoryQuery>,
) -> Result<Json<ApiResponse<Vec<WebSegmentHistoryPoint>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let mins = q.minutes.unwrap_or(30);
    let start_ts = Utc::now() - chrono::Duration::minutes(mins);

    let rows = sqlx::query(
        "SELECT h.ts, h.temp_avg
         FROM segment_history_1m h
         JOIN segment s ON s.id = h.segment_id
         WHERE s.dts_ch = $1 AND s.dts_code = $2 AND h.ts >= $3
         ORDER BY h.ts ASC",
    )
    .bind(q.dts_ch)
    .bind(q.dts_code)
    .bind(start_ts)
    .fetch_all(&st.pool)
    .await?;

    let data = rows
        .into_iter()
        .map(|r| {
            let ts: DateTime<Utc> = r.get("ts");
            WebSegmentHistoryPoint {
                time: ts.format("%H:%M").to_string(),
                temp: r.get("temp_avg"),
            }
        })
        .collect();

    Ok(Json(ApiResponse::ok("Segment history retrieved", data)))
}

#[derive(Debug, Serialize)]
pub struct WebSystemLog {
    pub id: i64,
    pub timestamp: String,
    pub event_type: String,
    pub message: String,
}

/// GET /api/v1/logs/system
pub async fn system_logs(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<Vec<WebSystemLog>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = sqlx::query("SELECT id, occurred_at, event_type, message FROM system_log ORDER BY id DESC LIMIT 500")
        .fetch_all(&st.pool)
        .await?;

    let data = rows
        .into_iter()
        .map(|r| {
            let dt: DateTime<Utc> = r.get("occurred_at");
            WebSystemLog {
                id: r.get("id"),
                timestamp: dt.to_rfc3339(),
                event_type: r.get("event_type"),
                message: r.get("message"),
            }
        })
        .collect();

    Ok(Json(ApiResponse::ok("System logs retrieved", data)))
}

#[derive(Debug, Deserialize)]
pub struct WriteLogRequest {
    pub event_type: String,
    pub message: String,
}

/// POST /api/v1/logs/system
pub async fn write_system_log(
    State(st): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<WriteLogRequest>,
) -> Result<Json<ApiResponse<()>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    sqlx::query("INSERT INTO system_log (event_type, message) VALUES ($1, $2)")
        .bind(&body.event_type)
        .bind(&body.message)
        .execute(&st.pool)
        .await?;
    Ok(Json(ApiResponse::ok("Log recorded", ())))
}

/// GET /api/v1/settings/all
pub async fn get_all_settings(
    State(st): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ApiResponse<std::collections::HashMap<String, String>>>, AppError> {
    authenticate_reader(&st.pool, &headers).await?;
    let rows = sqlx::query("SELECT key, value FROM site_setting")
        .fetch_all(&st.pool)
        .await?;
    let mut map = std::collections::HashMap::new();
    // Default fallback
    map.insert("warning_threshold".into(), "60.0".into());
    map.insert("critical_threshold".into(), "70.0".into());

    for r in rows {
        let k: String = r.get("key");
        let v: String = r.get("value");
        map.insert(k, v);
    }
    Ok(Json(ApiResponse::ok("Settings retrieved", map)))
}
