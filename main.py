import os
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

APP_NAME = os.getenv("APP_NAME", "TelegramBotBackend")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title=APP_NAME,
    debug=DEBUG_MODE,
    version="1.0.0"
)

pending_plans: Dict[str, Dict[str, Any]] = {}

def validate_int(value: Any, field: str) -> int:
    if not isinstance(value, int):
        raise HTTPException(status_code=400, detail=f"{field} must be an integer")
    return value

def validate_str(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"{field} must be a string")
    return value

@app.post("/process_request")
async def process_request(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    user_id = validate_int(payload.get("user_id"), "user_id")
    prompt = validate_str(payload.get("prompt"), "prompt")

    if "code" in prompt.lower():
        plan_id = str(uuid.uuid4())
        plan_summary = (
            f"Awaiting approval for a code-related request from user {user_id}. "
            "Review required before execution."
        )

        pending_plans[plan_id] = {
            "user_id": user_id,
            "prompt": prompt,
            "plan_summary": plan_summary
        }

        return JSONResponse(
            status_code=200,
            content={
                "status": "awaiting_approval",
                "message": "Plan generated, please approve to continue.",
                "data": {
                    "plan_summary": plan_summary,
                    "plan_id": plan_id
                }
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Request processed successfully."
            }
        )

@app.post("/approve_plan")
async def approve_plan(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    plan_id = validate_str(payload.get("plan_id"), "plan_id")
    user_id = validate_int(payload.get("user_id"), "user_id")

    if plan_id not in pending_plans:
        raise HTTPException(status_code=404, detail="Plan not found or already approved")

    stored_plan = pending_plans[plan_id]
    if stored_plan["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User not authorized to approve this plan")

    plan_summary = stored_plan["plan_summary"]
    del pending_plans[plan_id]

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Plan approved successfully",
            "plan_id": plan_id,
            "plan_summary": plan_summary
        }
    )

@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "message": exc.detail
        }
    )
