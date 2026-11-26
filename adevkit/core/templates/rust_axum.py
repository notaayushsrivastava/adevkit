from typing import List
from .base import BaseTemplate

class RustAxumTemplate(BaseTemplate):
    id = "rust_axum"
    name = "Rust Web API / Microservice (Axum + Tokio + Tower)"
    short_name = "Rust Web API (Axum)"
    description = "Blazing-fast async web service with Axum 0.7, Tokio, Tower-HTTP CORS/Trace middleware, Serde JSON, and health endpoints."
    category = "Backend / API"
    has_node = False
    has_python = False
    has_rust = True

    def scaffold(self) -> List[str]:
        files_created = []

        # Cargo.toml
        cargo_toml = """[package]
name = "{{PROJECT_NAME_LOWER}}"
version = "0.1.0"
edition = "2021"
authors = ["{{AUTHOR}}"]
description = "{{PROJECT_NAME}} - Powered by Axum & Aayush's DevKit"

[dependencies]
axum = "0.7"
tokio = { version = "1.40", features = ["full"] }
tower = { version = "0.5", features = ["util"] }
tower-http = { version = "0.6", features = ["cors", "trace"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[dev-dependencies]
tower = { version = "0.5", features = ["util"] }
http-body-util = "0.1"
"""
        self.write_file("Cargo.toml", cargo_toml)
        files_created.append("Cargo.toml")

        # src/main.rs
        main_rs = """use axum::{
    extract::Query,
    response::Json,
    routing::get,
    Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tower_http::trace::TraceLayer;
use tracing::info;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
    version: &'static str,
}

#[derive(Deserialize)]
struct HelloQuery {
    name: Option<String>,
}

#[derive(Serialize)]
struct HelloResponse {
    message: String,
    timestamp_epoch_secs: u64,
}

async fn health_check() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok",
        service: "{{PROJECT_NAME}}",
        version: "0.1.0",
    })
}

async fn hello_handler(Query(params): Query<HelloQuery>) -> Json<HelloResponse> {
    let name = params.name.unwrap_or_else(|| "World".to_string());
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    Json(HelloResponse {
        message: format!("Hello, {}! Welcome to {{PROJECT_NAME}}.", name),
        timestamp_epoch_secs: now,
    })
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/hello", get(hello_handler))
        .layer(TraceLayer::new_for_http());

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    info!("Starting server on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_health_check() {
        let res = health_check().await;
        assert_eq!(res.status, "ok");
        assert_eq!(res.version, "0.1.0");
    }
}
"""
        self.write_file("src/main.rs", main_rs)
        files_created.append("src/main.rs")

        # .gitignore
        gitignore = """/target
**/*.rs.bk
*.pdb
.env
"""
        self.write_file(".gitignore", gitignore)
        files_created.append(".gitignore")

        # README.md
        readme = """# {{PROJECT_NAME}}

High-performance asynchronous Rust Web API built with **[Axum](https://github.com/tokio-rs/axum)** and **[adevkit](https://github.com/notaayushsrivastava/adevkit)**.

## Endpoints

- `GET /health` - System healthcheck endpoint
- `GET /api/hello?name=Aayush` - Sample JSON greeting API

## Running Locally

```bash
# Start API server on http://127.0.0.1:3000
cargo run
```

Test with curl:
```bash
curl http://127.0.0.1:3000/health
curl "http://127.0.0.1:3000/api/hello?name=Aayush"
```

## Running Tests
```bash
cargo test
```

## Managing Dependencies
```bash
adevkit add sqlx
adevkit add reqwest
adevkit deps list
```
"""
        self.write_file("README.md", readme)
        files_created.append("README.md")

        return files_created
