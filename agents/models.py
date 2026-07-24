from pydantic import BaseModel
from typing import List, Optional

class Prompt(BaseModel):
    text: str

class Task(BaseModel):
    description: str
    agent: str

class WorkflowPlan(BaseModel):
    tasks: List[Task]
    next_agent: str
    status: str = "pending"

class ApprovalRequest(BaseModel):
    task_id: str
    description: str

class ApprovalResponse(BaseModel):
    approved: bool
    comment: Optional[str] = None
