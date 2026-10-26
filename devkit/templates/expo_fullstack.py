from pathlib import Path
from typing import List
from .base import BaseTemplate

class ExpoFullstackTemplate(BaseTemplate):
    id = "expo_fullstack"
    name = "Full-Stack Expo Mobile + Backend Monorepo (frontend/ & backend/)"
    description = "Monorepo with Expo React Native mobile frontend/ and selectable backend/ (FastAPI or Hono Node.js)."
    category = "Mobile / Full-Stack"

    def __init__(self, project_name: str, target_dir: Path, backend_stack: str = "fastapi", author: str = "Aayush"):
        super().__init__(project_name, target_dir, author)
        self.backend_stack = backend_stack.lower()
        self.has_node = True
        self.has_python = "fastapi" in self.backend_stack or "python" in self.backend_stack

    def scaffold(self) -> List[str]:
        files_created = []

        # 1. Root Monorepo package.json
        backend_dev_cmd = (
            "cd backend && uvicorn app.main:app --reload --port 8000"
            if self.has_python
            else "npm run dev --prefix backend"
        )
        root_pkg = f"""{{
  "name": "{{{{PROJECT_NAME_LOWER}}}}-monorepo",
  "version": "1.0.0",
  "private": true,
  "scripts": {{
    "dev:mobile": "npm start --prefix frontend",
    "dev:backend": "{backend_dev_cmd}",
    "dev": "npm run dev:mobile"
  }}
}}"""
        self.write_file("package.json", root_pkg)
        files_created.append("package.json")

        # 2. Frontend (Expo App)
        # frontend/package.json
        fe_pkg = """{
  "name": "{{PROJECT_NAME_LOWER}}-mobile",
  "version": "1.0.0",
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~51.0.0",
    "expo-constants": "~16.0.2",
    "expo-linking": "~6.3.1",
    "expo-router": "~3.5.23",
    "expo-status-bar": "~1.12.1",
    "react": "18.2.0",
    "react-native": "0.74.5",
    "react-native-safe-area-context": "4.10.5",
    "react-native-screens": "3.31.1"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.45",
    "typescript": "~5.3.3"
  },
  "private": true
}"""
        self.write_file("frontend/package.json", fe_pkg)
        files_created.append("frontend/package.json")

        # frontend/app.json
        fe_app_json = """{
  "expo": {
    "name": "{{PROJECT_NAME}}",
    "slug": "{{PROJECT_NAME_LOWER}}",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "dark",
    "scheme": "{{PROJECT_NAME_LOWER}}",
    "plugins": ["expo-router"],
    "ios": { "supportsTablet": true }
  }
}"""
        self.write_file("frontend/app.json", fe_app_json)
        files_created.append("frontend/app.json")

        # frontend/app/_layout.tsx
        fe_layout = """import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: '#090d16' },
          headerTintColor: '#fff',
          contentStyle: { backgroundColor: '#090d16' },
        }}
      />
    </>
  );
}
"""
        self.write_file("frontend/app/_layout.tsx", fe_layout)
        files_created.append("frontend/app/_layout.tsx")

        # frontend/app/index.tsx
        fe_index = """import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useState, useEffect } from 'react';

export default function HomeScreen() {
  const [apiStatus, setApiStatus] = useState<string>('Connecting to backend...');

  useEffect(() => {
    // Attempt local API ping
    fetch('http://127.0.0.1:8000/health')
      .then((res) => res.json())
      .then((data) => setApiStatus(`Backend: ${data.status || 'OK'}`))
      .catch(() => setApiStatus('Backend offline (Run backend server)'));
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{{PROJECT_NAME}}</Text>
      <Text style={styles.subtitle}>Expo Mobile + Backend Monorepo</Text>
      <View style={styles.statusBadge}>
        <Text style={styles.statusText}>{apiStatus}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#090d16',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  subtitle: {
    fontSize: 16,
    color: '#94a3b8',
    marginTop: 8,
  },
  statusBadge: {
    marginTop: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  statusText: {
    color: '#38bdf8',
    fontSize: 14,
    fontFamily: 'monospace',
  },
});
"""
        self.write_file("frontend/app/index.tsx", fe_index)
        files_created.append("frontend/app/index.tsx")

        # 3. Backend Setup
        if self.has_python:
            # Python FastAPI Backend in backend/
            reqs = "fastapi>=0.115.0\nuvicorn[standard]>=0.32.0\npydantic>=2.9.0\npytest>=8.3.0\nhttpx>=0.27.2\n"
            self.write_file("backend/requirements.txt", reqs)
            files_created.append("backend/requirements.txt")

            pyproject = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{PROJECT_NAME_LOWER}}-backend"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
"""
            self.write_file("backend/pyproject.toml", pyproject)
            files_created.append("backend/pyproject.toml")

            main_py = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{{PROJECT_NAME}} API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "{{PROJECT_NAME}} Mobile API"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "mobile-backend"}
"""
            self.write_file("backend/app/main.py", main_py)
            files_created.append("backend/app/main.py")

            test_py = """from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
"""
            self.write_file("backend/tests/test_main.py", test_py)
            files_created.append("backend/tests/test_main.py")
        else:
            # Node / Hono Backend in backend/
            node_be_pkg = """{
  "name": "{{PROJECT_NAME_LOWER}}-backend",
  "type": "module",
  "version": "0.1.0",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc"
  },
  "dependencies": {
    "hono": "^4.6.0",
    "@hono/node-server": "^1.13.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.6.3",
    "@types/node": "^22.8.1"
  }
}"""
            self.write_file("backend/package.json", node_be_pkg)
            files_created.append("backend/package.json")

            index_ts = """import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { serve } from '@hono/node-server';

const app = new Hono();
app.use('*', cors());

app.get('/', (c) => c.json({ message: '{{PROJECT_NAME}} API' }));
app.get('/health', (c) => c.json({ status: 'healthy', service: 'mobile-backend' }));

const port = 8000;
console.log(`Mobile backend running at http://localhost:${port}`);
serve({ fetch: app.fetch, port });
"""
            self.write_file("backend/src/index.ts", index_ts)
            files_created.append("backend/src/index.ts")

        # Root .env.example
        self.write_file(".env.example", "API_BASE_URL=\"http://127.0.0.1:8000\"\n")
        files_created.append(".env.example")

        return files_created
