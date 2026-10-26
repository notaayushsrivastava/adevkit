from pathlib import Path
from devkit.scaffold.agent_configs import scaffold_agent_configs, SUPPORTED_AGENTS


def test_scaffold_all_agent_configs(tmp_path):
    target = tmp_path / "agent_test_project"
    target.mkdir()

    all_agents = list(SUPPORTED_AGENTS.keys())
    created = scaffold_agent_configs(
        target_dir=target,
        project_name="agent_test_project",
        template_id="nextjs",
        installed_skills=["impeccable", "ponytail"],
        selected_agents=all_agents,
    )

    # Verify Antigravity
    assert (target / "AGENTS.md").exists()

    # Verify Cursor
    assert (target / ".cursorrules").exists()
    assert (target / ".cursor" / "rules" / "main.mdc").exists()

    # Verify Claude Code
    assert (target / "CLAUDE.md").exists()
    claude_txt = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Common Commands" in claude_txt

    # Verify GitHub Copilot
    assert (target / ".github" / "copilot-instructions.md").exists()

    # Verify Windsurf
    assert (target / ".windsurfrules").exists()

    # Verify Aider
    assert (target / ".aider.conf.yml").exists()

    assert len(created) >= 6
