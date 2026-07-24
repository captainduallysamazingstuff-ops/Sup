import asyncio
import logging
import requests
from bs4 import BeautifulSoup
from .models import ApprovalRequest, ApprovalResponse
from .utils import setup_logger

logger = setup_logger("/tmp/agent_orchestrator.log")

class ScraperAgent:
    """
    Retrieves content from a target URL, extracts headlines and paragraphs,
    and formats them as markdown.
    """
    def __init__(self, target_url: str = "https://pytorch.org/news/"):
        self.target_url = target_url
        self.output_path: str | None = None

    async def fetch_and_extract(self) -> str:
        try:
            resp = requests.get(self.target_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch URL", exc_info=exc)
            raise

        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = [h.get_text(strip=True) for h in soup.find_all("h1")]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        content = "\n".join(headlines + paragraphs)
        return content

    async def write_markdown(self, markdown: str, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(markdown)
            logger.info("Wrote markdown to %s", path)
        except OSError as exc:
            logger.error("Failed to write markdown file", exc_info=exc)
            raise

    async def run(self, request: ApprovalRequest) -> str:
        """
        Execute the scrape and write steps.
        Returns the path to the generated markdown file.
        """
        markdown = await self.fetch_and_extract()
        if self.output_path is None:
            self.output_path = "/output/news.md"
        await self.write_markdown(markdown, self.output_path)
        logger.info("Scraper completed for task %s", request.task_id)
        return self.output_path

    async def start(self) -> None:
        pass
