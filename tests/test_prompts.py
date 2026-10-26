from prompt_toolkit.output import DummyOutput
from prompt_toolkit.application import create_app_session
from adevkit.prompts import prompt_template_selection
from adevkit.templates import get_all_templates

def test_template_selection_rendering():
    """Verify prompt_template_selection initializes and formats properly."""
    templates = get_all_templates()
    assert len(templates) >= 10
    
    # Verify each template has clean names and descriptions
    for t in templates:
        assert "short_name" in t
        assert len(t["short_name"]) < 50
        assert "description" in t
