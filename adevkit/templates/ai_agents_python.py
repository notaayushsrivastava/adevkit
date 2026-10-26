from typing import List
from .base import BaseTemplate

class AiAgentsPythonTemplate(BaseTemplate):
    id = "ai_agents_python"
    name = "AI Agent / Multi-Agent Backend (Python + FastAPI + LangGraph)"
    short_name = "AI Agent Backend (LangGraph + FastAPI)"
    description = "Asynchronous multi-agent framework starter with state graphs, tool routing, memory, and FastAPI endpoints."
    category = "AI / Agentic"
    has_node = False
    has_python = True

    def scaffold(self) -> List[str]:
        files_created = []

        # requirements.txt
        reqs = """fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.9.0
pydantic-settings>=2.6.0
google-genai>=0.1.0
langgraph>=0.2.34
langchain-core>=0.3.10
python-dotenv>=1.0.1
rich>=13.9.0
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
description = "{{PROJECT_NAME}} - Multi-Agent AI System"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
"""
        self.write_file("pyproject.toml", pyproject)
        files_created.append("pyproject.toml")

        # app/agents/graph.py (StateGraph / multi-agent workflow)
        graph_py = """from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel

class AgentState(TypedDict):
    input_prompt: str
    plan: List[str]
    current_step: int
    tool_results: Dict[str, str]
    final_output: str

def planner_node(state: AgentState) -> Dict:
    \"\"\"Planner agent decomposes prompt into structured tasks.\"\"\"
    prompt = state.get("input_prompt", "")
    return {
        "plan": [
            f"Analyze requirements for: {prompt}",
            "Synthesize domain context and knowledge",
            "Generate structured response",
        ],
        "current_step": 0,
    }

def executor_node(state: AgentState) -> Dict:
    \"\"\"Execution agent runs each step and populates final output.\"\"\"
    plan = state.get("plan", [])
    output = f"Successfully executed plan with {len(plan)} steps."
    return {"final_output": output}
"""
        self.write_file("app/agents/graph.py", graph_py)
        files_created.append("app/agents/graph.py")

        # app/main.py
        main_py = """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.graph import planner_node, executor_node, AgentState
import uvicorn

app = FastAPI(
    title="{{PROJECT_NAME}} - Multi-Agent Engine",
    version="0.1.0",
)

class RunAgentRequest(BaseModel):
    prompt: str

class RunAgentResponse(BaseModel):
    status: str
    plan: list[str]
    output: str

@app.get("/")
def root():
    return {"status": "online", "app": "{{PROJECT_NAME}}"}

@app.post("/agent/run", response_model=RunAgentResponse)
def run_agent(req: RunAgentRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    state: AgentState = {
        "input_prompt": req.prompt,
        "plan": [],
        "current_step": 0,
        "tool_results": {},
        "final_output": "",
    }
    
    # Run planner and executor pipeline
    state.update(planner_node(state))
    state.update(executor_node(state))

    return RunAgentResponse(
        status="completed",
        plan=state["plan"],
        output=state["final_output"],
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
"""
        self.write_file("app/main.py", main_py)
        files_created.append("app/main.py")

        # tests/test_agent.py
        test_py = """from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_run_agent():
    res = client.post("/agent/run", json={"prompt": "Design high-scale caching"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert len(data["plan"]) == 3
"""
        self.write_file("tests/test_agent.py", test_py)
        files_created.append("tests/test_agent.py")

        # .env.example
        self.write_file(".env.example", "GEMINI_API_KEY=\"your_gemini_api_key\"\nAPP_ENV=\"development\"\n")
        files_created.append(".env.example")

        return files_created
