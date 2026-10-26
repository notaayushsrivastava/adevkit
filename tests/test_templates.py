import tempfile
from pathlib import Path
import pytest
from devkit.templates import (
    BUILTIN_TEMPLATES,
    NextjsTemplate,
    PythonFastAPITemplate,
    ViteReactTemplate,
    MinimalAgenticTemplate,
    ExpoMobileTemplate,
)

def test_nextjs_template_scaffolding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl = NextjsTemplate(project_name="Awesome App", target_dir=Path(tmpdir))
        files = tmpl.scaffold()
        assert "package.json" in files
        assert "app/page.tsx" in files
        assert "tailwind.config.ts" in files

        # Verify placeholder replacement
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
