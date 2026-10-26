from typing import List
from .base import BaseTemplate

class PythonFastAPITemplate(BaseTemplate):
    id = "python_fastapi"
    name = "Python Backend / API (FastAPI + Typer + venv)"
    short_name = "Python Backend / API (FastAPI)"
    description = "Modern Python 3.10+ async backend with FastAPI, Pydantic v2, Typer CLI, pytest, and auto-configured venv."
    category = "Backend / API"
    has_node = False
    has_python = True

    def scaffold(self) -> List[str]:
        files_created = []

        # requirements.txt
        reqs = """fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.9.0
pydantic-settings>=2.6.0
typer>=0.12.5
rich>=13.9.0
python-dotenv>=1.0.1
pytest>=8.3.0
httpx>=0.27.2
"""
        self.write_file("requirements.txt", reqs)
        files_created.append("requirements.txt")

        # pyproject.toml
        pyproject = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{PROJECT_NAME_LOWER}}"
version = "0.1.0"
description = "{{PROJECT_NAME}} - Powered by FastAPI & Aayush's DevKit"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "typer>=0.12.5",
    "rich>=13.9.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
"""
        self.write_file("pyproject.toml", pyproject)
        files_created.append("pyproject.toml")

        # app/__init__.py
        self.write_file("app/__init__.py", '"""{{PROJECT_NAME}} Application Package."""\n__version__ = "0.1.0"\n')
        files_created.append("app/__init__.py")

        # app/main.py
        main_py = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="{{PROJECT_NAME}}",
    description="API built with FastAPI and Aayush's DevKit",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    app: str

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to {{PROJECT_NAME}} API",
        "docs_url": "/docs",
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(status="healthy", app="{{PROJECT_NAME}}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
"""
        self.write_file("app/main.py", main_py)
        files_created.append("app/main.py")

        # tests/test_main.py
        test_py = """from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
"""
        self.write_file("tests/test_main.py", test_py)
        files_created.append("tests/test_main.py")

        # .env.example
        self.write_file(".env.example", "APP_ENV=development\nPORT=8000\nHOST=127.0.0.1\n")
        files_created.append(".env.example")

        return files_created
