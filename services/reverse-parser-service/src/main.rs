mod ir_converter;
mod parser;

use axum::{routing::{get, post}, Json, Router};
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Deserialize)]
struct ParseReq { hcl: String }

async fn parse(Json(req): Json<ParseReq>) -> Result<Json<Value>, (axum::http::StatusCode, String)> {
    if req.hcl.len() > 2_000_000 { return Err((axum::http::StatusCode::PAYLOAD_TOO_LARGE, "too large".into())); }
    let body = parser::hcl_parser::parse(&req.hcl).map_err(|e| (axum::http::StatusCode::UNPROCESSABLE_ENTITY, e))?;
    Ok(Json(json!({ "ir": ir_converter::hcl_to_ir::convert(&body) })))
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/parse", post(parse))
        .route("/health", get(|| async { Json(json!({"status":"ok","service":"reverse-parser"})) }));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8004").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
