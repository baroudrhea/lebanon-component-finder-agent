"""
FastAPI wrapper around agent.py's run_agent() function.

This exists so the n8n custom node (written in TypeScript/Node.js, since
that's the only language n8n nodes support) can call the existing Python
agent over a simple HTTP request, without rewriting any agent logic.

agent.py itself is completely untouched -- this file just exposes
run_agent() as a POST endpoint.

Homework 4, Part B.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the existing, already-tested agent code unchanged.
from agent import run_agent

app = FastAPI(title="Component Finder Agent API")


class AgentRequest(BaseModel):
    message: str    # the component the user is searching for
    api_key: str     # Gemini API key, passed through from n8n's credential store


class AgentResponse(BaseModel):
    answer: str


@app.post("/run-agent", response_model=AgentResponse)
def run_agent_endpoint(req: AgentRequest):
    """
    Runs the full agent loop for one query and returns the final answer.
    Mirrors exactly what agent.py's __main__ loop does per input line.
    """
    if not req.message:
        raise HTTPException(status_code=400, detail="Missing 'message'")
    if not req.api_key:
        raise HTTPException(status_code=400, detail="Missing 'api_key'")

    try:
        answer = run_agent(req.message, req.api_key)
    except Exception as e:
        # Surface agent/Gemini errors as a clean HTTP 500 instead of crashing
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return AgentResponse(answer=answer)


@app.get("/health")
def health():
    """Simple check so you can confirm the service is up before wiring n8n to it."""
    return {"status": "ok"}
