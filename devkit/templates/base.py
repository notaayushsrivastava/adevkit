from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List

class BaseTemplate(ABC):
    id: str = "base"
    name: str = "Base Template"
    short_name: str = ""
    description: str = "Base project template"
    category: str = "General"
    has_node: bool = False
    has_python: bool = False

    def __init__(self, project_name: str, target_dir: Path, author: str = "Aayush"):
        self.project_name = project_name
        self.target_dir = Path(target_dir)
        self.author = author

    def render_text(self, content: str) -> str:
        """Replace template variables."""
        return (
            content.replace("{{PROJECT_NAME}}", self.project_name)
            .replace("{{PROJECT_NAME_LOWER}}", self.project_name.lower().replace(" ", "-").replace("_", "-"))
            .replace("{{AUTHOR}}", self.author)
        )

    def write_file(self, relative_path: str, content: str) -> Path:
        """Write a file inside target_dir creating parent directories if needed."""
        dest = self.target_dir / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.render_text(content), encoding="utf-8")
        return dest

    @abstractmethod
    def scaffold(self) -> List[str]:
        """Scaffold template files into target_dir. Returns list of created file paths."""
        pass
