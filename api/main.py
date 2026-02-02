# third
from fastapi import FastAPI

# internal
from api.schemas import AgentRequest, AgentResponse

app = FastAPI(
    title="Conversational Business Analytics - Agentic AI API",
    version="0.1.0",
)


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    """
    Endpoint to run the agent with the provided request.
    """
    # TEMP: stub implementation
    return AgentResponse(run_id=request.run_id, output=f"Agent received: {request.input}", metadata={"status": "stub"})


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
