from typing import Dict, Type, List
from .base import BaseTemplate
from .nextjs import NextjsTemplate
from .python_fastapi import PythonFastAPITemplate
from .vite_react import ViteReactTemplate
from .minimal_agentic import MinimalAgenticTemplate
from .expo_mobile import ExpoMobileTemplate
from .custom import CustomProjectTemplate, list_custom_templates, save_custom_template, delete_custom_template

BUILTIN_TEMPLATES: Dict[str, Type[BaseTemplate]] = {
    "nextjs": NextjsTemplate,
    "python_fastapi": PythonFastAPITemplate,
    "vite_react": ViteReactTemplate,
    "minimal_agentic": MinimalAgenticTemplate,
    "expo_mobile": ExpoMobileTemplate,
}

def get_all_templates() -> List[Dict]:
    """Return all available templates including built-in and user-created custom templates."""
    templates = []
    for tid, cls in BUILTIN_TEMPLATES.items():
        templates.append({
            "id": tid,
            "name": cls.name,
            "description": cls.description,
            "category": cls.category,
            "is_custom": False,
            "has_node": cls.has_node,
            "has_python": cls.has_python,
        })

    for c in list_custom_templates():
        templates.append({
            "id": f"custom:{c['id']}",
            "name": f"✨ {c['name']} (Custom)",
            "description": c["description"],
            "category": "Custom",
            "is_custom": True,
            "has_node": c["has_node"],
            "has_python": c["has_python"],
            "custom_data": c,
        })

    return templates

__all__ = [
    "BaseTemplate",
    "NextjsTemplate",
    "PythonFastAPITemplate",
    "ViteReactTemplate",
    "MinimalAgenticTemplate",
    "ExpoMobileTemplate",
    "CustomProjectTemplate",
    "BUILTIN_TEMPLATES",
    "get_all_templates",
    "list_custom_templates",
    "save_custom_template",
    "delete_custom_template",
]
