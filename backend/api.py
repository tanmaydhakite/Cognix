from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.autonomous_agent import AutonomousAgent

from backend.response_formatter import clean_response

app = FastAPI(
    title="Cognix API",
    description="Autonomous everyday-task agent",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


agent = AutonomousAgent(max_replans=2)


class GoalRequest(BaseModel):
    goal: str


@app.get("/")
def root():

    return {
        "status": "online",
        "message": "Cognix backend is running"
    }


@app.post("/run")
def run_agent(request: GoalRequest):

    goal = request.goal.strip()

    if not goal:

        return {
            "success": False,
            "error": "Goal cannot be empty."
        }

    try:

        results = agent.run(goal)

        # Check whether the agent is waiting for approval
        for item in results:

            execution = item.get("execution", {})

            if execution.get("requires_confirmation"):

                return {
                    "success": True,
                    "status": "waiting_for_confirmation",
                    "goal": goal,
                    "results": results,
                    "confirmation": execution
                }

        cleaned_results = clean_response(str(results))

        return {
            "success": True,
            "status": "completed",
            "goal": goal,
            "response": cleaned_results,
            "results": results
        }

    except Exception as error:

        return {
            "success": False,
            "goal": goal,
            "error": str(error)
        }


# ============================================================
# CONFIRMATION
# ============================================================

@app.get("/confirmation")
def get_confirmation():

    pending = agent.executor.get_pending_confirmation()

    if not pending:

        return {
            "pending": False
        }

    return {
        "pending": True,
        "action": pending
    }


@app.post("/confirmation/approve")
def approve_confirmation():

    # First execute the approved action
    result = agent.executor.confirm_pending_action()

    if not result.get("success"):
        return result

    # Then resume remaining steps
    resume_result = agent.resume_after_approval()

    return {
    "success": True,
    "approved": True,
    "response": clean_response(
        str(resume_result)
    ),
    "result": result,
    "resume": resume_result
}


@app.post("/confirmation/cancel")
def cancel_confirmation():

    result = agent.executor.cancel_pending_action()

    return result