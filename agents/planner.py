import asyncio
import json
import logging
from typing import List
from .models import Prompt, Task, WorkflowPlan
from .utils import setup_logger

logger = setup_logger("/tmp/agent_orchestrator.log")

class PlannerAgent:
    """
    Decomposes a user prompt into discrete tasks and creates a WorkflowPlan.
    """
    def __init__(self, plan_file: str = "/tmp/workflow_plan.json"):
        self.plan_file = plan_file

    async def parse_prompt(self, prompt: Prompt) -> WorkflowPlan:
        tasks: List[Task] = []
        text = prompt.text.lower()

        if "scrape" in text or "extract" in text:
            tasks.append(Task(description="scrape pyTorch news", agent="scraper"))
        if "save" in text or "store" in text:
            tasks.append(Task(description="save markdown to file", agent="file_writer"))
        if "schedule" in text or "run" in text:
            tasks.append(Task(description="schedule recurring job", agent="scheduler"))

        next_agent = tasks[0].agent if tasks else "scheduler"
        plan = WorkflowPlan(tasks=tasks, next_agent=next_agent, status="pending")

        with open(self.plan_file, "w") as f:
            json.dump(plan.dict(), f)

        logger.info("Generated workflow plan: %s", plan)
        return plan

    async def start(self, prompt: Prompt) -> WorkflowPlan:
        return await self.parse_prompt(prompt)
