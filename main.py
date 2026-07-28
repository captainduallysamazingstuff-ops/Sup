import logging
from fastapi import FastAPI
from agents.planner import PlanningAgent
from agents.scraper import ScrapingAgent
from agents.file_writer import FileWriterAgent
from agents.scheduler import SchedulerAgent

logging.basicConfig(level=logging.INFO)
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
