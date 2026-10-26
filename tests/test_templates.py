import tempfile
from pathlib import Path
import pytest
from adevkit.templates import (
    BUILTIN_TEMPLATES,
    NextjsTemplate,
    PythonFastAPITemplate,
    ViteReactTemplate,
    MinimalAgenticTemplate,
    ExpoMobileTemplate,
    SaasFullstackTemplate,
    DesignSystemTemplate,
    ContentSiteTemplate,
    AiAgentsPythonTemplate,
    ExpoFullstackTemplate,
)

def test_nextjs_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = NextjsTemplate(project_name="Awesome App", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "app/page.tsx" in files
        assert "tailwind.config.ts" in files
        page_content = (Path(tmpdir) / "app" / "page.tsx").read_text(encoding="utf-8")
        assert "Awesome App" in page_content

def test_python_fastapi_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = PythonFastAPITemplate(project_name="Data Core", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "requirements.txt" in files
        assert "app/main.py" in files
        assert "tests/test_main.py" in files
        main_content = (Path(tmpdir) / "app" / "main.py").read_text(encoding="utf-8")
        assert "Data Core" in main_content

def test_vite_react_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = ViteReactTemplate(project_name="Vite Client", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "vite.config.ts" in files
        assert "src/App.tsx" in files

def test_minimal_agentic_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = MinimalAgenticTemplate(project_name="AI Brain", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "README.md" in files
        content = (Path(tmpdir) / "README.md").read_text(encoding="utf-8")
        assert "AI Brain" in content

def test_expo_mobile_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = ExpoMobileTemplate(project_name="FitTrack", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "app.json" in files
        assert "App.tsx" in files

def test_saas_fullstack_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = SaasFullstackTemplate(project_name="SaaS Pro", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "prisma/schema.prisma" in files
        assert "app/page.tsx" in files
        content = (Path(tmpdir) / "app" / "page.tsx").read_text(encoding="utf-8")
        assert "SaaS Pro" in content

def test_design_system_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = DesignSystemTemplate(project_name="Aura UI", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "src/tokens/index.ts" in files
        assert "src/components/Button.tsx" in files
        assert "src/App.tsx" in files

def test_content_site_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = ContentSiteTemplate(project_name="Design Journal", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "astro.config.mjs" in files
        assert "src/pages/index.astro" in files
        content = (Path(tmpdir) / "src/pages/index.astro").read_text(encoding="utf-8")
        assert "Design Journal" in content

def test_ai_agents_python_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = AiAgentsPythonTemplate(project_name="Agent Swarm", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "requirements.txt" in files
        assert "app/agents/graph.py" in files
        assert "app/main.py" in files
        assert "tests/test_agent.py" in files

def test_expo_fullstack_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test with FastAPI backend
        tmpl = ExpoFullstackTemplate(project_name="Fleet Track", target_dir=Path(tmpdir), backend_stack="fastapi")
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "frontend/package.json" in files
        assert "frontend/app/index.tsx" in files
        assert "backend/requirements.txt" in files
        assert "backend/app/main.py" in files
