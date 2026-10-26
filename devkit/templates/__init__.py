from typing import Dict, Type, List
from .base import BaseTemplate
from .nextjs import NextjsTemplate
from .python_fastapi import PythonFastAPITemplate
from .vite_react import ViteReactTemplate
from .minimal_agentic import MinimalAgenticTemplate
from .expo_mobile import ExpoMobileTemplate
from .saas_fullstack import SaasFullstackTemplate
from .design_system import DesignSystemTemplate
from .content_site import ContentSiteTemplate
from .ai_agents_python import AiAgentsPythonTemplate
from .expo_fullstack import ExpoFullstackTemplate
from .custom import CustomProjectTemplate, list_custom_templates, save_custom_template, delete_custom_template

BUILTIN_TEMPLATES: Dict[str, Type[BaseTemplate]] = {
    "nextjs": NextjsTemplate,
    "saas_fullstack": SaasFullstackTemplate,
    "design_system": DesignSystemTemplate,
    "content_site": ContentSiteTemplate,
    "python_fastapi": PythonFastAPITemplate,
    "ai_agents_python": AiAgentsPythonTemplate,
    "vite_react": ViteReactTemplate,
    "minimal_agentic": MinimalAgenticTemplate,
    "expo_mobile": ExpoMobileTemplate,
    "expo_fullstack": ExpoFullstackTemplate,
}

def get_all_templates() -> List[Dict]:
    """Return all available templates including built-in and user-created custom templates."""
    templates = []
    for tid, cls in BUILTIN_TEMPLATES.items():
        templates.append({
            "id": tid,
            "name": cls.name,
            "short_name": getattr(cls, "short_name", "") or cls.name,
            "description": cls.description,
            "category": cls.category,
            "is_custom": False,
            "has_node": cls.has_node,
            "has_python": cls.has_python,
        })

    for c in list_custom_templates():
        templates.append({
            "id": f"custom:{c['id']}",
            "name": f"* {c['name']} (Custom)",
            "short_name": f"* {c['name']} (Custom)",
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
    "SaasFullstackTemplate",
    "DesignSystemTemplate",
    "ContentSiteTemplate",
    "PythonFastAPITemplate",
    "AiAgentsPythonTemplate",
    "ViteReactTemplate",
    "MinimalAgenticTemplate",
    "ExpoMobileTemplate",
    "ExpoFullstackTemplate",
    "CustomProjectTemplate",
    "BUILTIN_TEMPLATES",
    "get_all_templates",
    "list_custom_templates",
    "save_custom_template",
    "delete_custom_template",
]
