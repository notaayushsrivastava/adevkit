from typing import List
from .base import BaseTemplate

class RustCliTemplate(BaseTemplate):
    id = "rust_cli"
    name = "Rust CLI Application (Clap + Tokio + Anyhow)"
    short_name = "Rust CLI (Clap + Tokio)"
    description = "Modern asynchronous Rust command-line tool with Clap v4 derive, Tokio runtime, Anyhow error handling, and structured logging."
    category = "Rust / Systems"
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
description = "{{PROJECT_NAME}} - Powered by Rust & Aayush's DevKit"

[dependencies]
clap = { version = "4.5", features = ["derive", "env"] }
tokio = { version = "1.40", features = ["full"] }
anyhow = "1.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[dev-dependencies]
assert_cmd = "2.0"
predicates = "3.1"
"""
        self.write_file("Cargo.toml", cargo_toml)
        files_created.append("Cargo.toml")

        # src/main.rs
        main_rs = """use anyhow::Result;
use clap::{Parser, Subcommand};
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[derive(Parser, Debug)]
#[command(
    name = "{{PROJECT_NAME_LOWER}}",
    author = "{{AUTHOR}}",
    version = "0.1.0",
    about = "{{PROJECT_NAME}} CLI - Powered by Aayush's DevKit",
    long_about = None
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    #[arg(short, long, global = true, help = "Enable verbose debug logging")]
    verbose: bool,
}

#[derive(Subcommand, Debug)]
enum Commands {
    #[command(about = "Display project information and status")]
    Info,

    #[command(about = "Run main application task")]
    Run {
        #[arg(short, long, default_value = "world", help = "Target name to greet")]
        name: String,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    let log_level = if cli.verbose { Level::DEBUG } else { Level::INFO };
    let subscriber = FmtSubscriber::builder()
        .with_max_level(log_level)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("Failed to initialize tracing subscriber");

    match cli.command {
        Some(Commands::Info) => {
            println!("{{PROJECT_NAME}} v0.1.0");
            println!("Built with Rust, Clap, Tokio & Aayush's DevKit");
        }
        Some(Commands::Run { name }) => {
            info!("Executing task for: {}", name);
            println!("Hello, {}! Task completed successfully.", name);
        }
        None => {
            println!("{{PROJECT_NAME}} - Use --help to view available commands.");
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cli_parsing() {
        let cli = Cli::parse_from(&["test-app", "run", "--name", "Rustacean"]);
        match cli.command {
            Some(Commands::Run { name }) => assert_eq!(name, "Rustacean"),
            _ => panic!("Expected Run subcommand"),
        }
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

Modern asynchronous Rust CLI application scaffolded with **[adevkit](https://github.com/notaayushsrivastava/adevkit)**.

## Quick Start

### Build and Run
```bash
# Run CLI help
cargo run -- --help

# Run info command
cargo run -- info

# Run main command with custom parameters
cargo run -- run --name "Developer"
```

### Running Tests
```bash
cargo test
```

### Managing Dependencies
Use adevkit to manage your Rust dependencies:
```bash
adevkit add regex
adevkit add tempfile --dev
adevkit deps list
```
"""
        self.write_file("README.md", readme)
        files_created.append("README.md")

        return files_created
