import logging
import os
from datetime import datetime

def setup_logger(log_path: str) -> logging.Logger:
    logger = logging.getLogger("agent_orchestrator")
    logger.setLevel(logging.INFO)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_info(logger: logging.Logger, msg: str) -> None:
    logger.info(msg)

def log_error(logger: logging.Logger, msg: str, exc: Exception | None = None) -> None:
    if exc:
        logger.error(msg, exc_info=exc)
    else:
        logger.error(msg)
