import asyncio
import logging
from pathlib import Path
from .models import ApprovalRequest
from .utils import setup_logger

logger = setup_logger("/tmp/agent_orchestrator.log")

class FileWriterAgent:
    """
    Copies a markdown file to a destination directory.
    """
    def __init__(self, dest_dir: str = "/output"):
        self.dest_dir = dest_dir

    async def write(self, source_path: str, request: ApprovalRequest) -> Path:
        src = Path(source_path)
        dest_dir = Path(self.dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / src.name
        try:
            dest_path.write_bytes(src.read_bytes())
            logger.info("File copied to %s", dest_path)
        except OSError as exc:
            logger.error("Failed to copy file", exc_info=exc)
            raise
        return dest_path

    async def start(self) -> None:
        pass
