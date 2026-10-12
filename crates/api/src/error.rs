use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use serde_json::json;

pub struct AppError(pub StatusCode, pub String);

impl AppError {
    pub fn unauthorized() -> Self {
        Self(StatusCode::UNAUTHORIZED, "Invalid authentication credentials or API key.".into())
    }
    pub fn forbidden() -> Self {
        Self(StatusCode::FORBIDDEN, "Access forbidden: insufficient permissions for this resource.".into())
    }
}

impl From<sqlx::Error> for AppError {
    fn from(e: sqlx::Error) -> Self {
        eprintln!("db error: {e}");
        Self(StatusCode::INTERNAL_SERVER_ERROR, "Internal database error occurred.".into())
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        (self.0, Json(json!({ "success": false, "message": self.1, "data": null }))).into_response()
    }
}
