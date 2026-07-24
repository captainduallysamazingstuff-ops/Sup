# AI Supervisor Factory

This project deploys an AI Supervisor system consisting of a backend, a Telegram bot, and several agents (planner, scraper, file writer, scheduler) using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- A Telegram bot token (create via [@BotFather](https://t.me/BotFather))
- A backend API URL (default: `http://localhost:8000`)

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/captainduallysamazingstuff-ops/Sup.git
cd Sup
```

### 2. Make the deploy script executable
```bash
chmod +x deploy.sh
```

### 3. Run the deployment script
This will prompt you for your Telegram bot token and backend URL:
```bash
./deploy.sh
```

### 4. Start the stack
```bash
./deploy.sh start
```

The script will:
- Build all Docker images
- Start services in detached mode
- Wait for all services to report healthy via `/health` endpoint

### 5. View logs
```bash
./deploy.sh logs
```

### 6. Check status
```bash
./deploy.sh status
```

### 7. Stop services
```bash
./deploy.sh stop
```

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required)
- `BACKEND_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `LOGS_DIR`: Directory for logs (default: `./logs`)

## Using the Bot

1. Open Telegram and find your bot
2. Send `/start` to see the welcome message
3. Send a message containing the word "code" to trigger the approval workflow
4. Press the **✅ Approve & Deploy** button to approve and execute

## Architecture

- **Backend**: FastAPI service (`main.py`) on port 8000
- **Telegram Bot**: Python bot (`bot.py`) connecting via `TELEGRAM_BOT_TOKEN`
- **Agents**: Four specialized services:
  - **Planner**: Decomposes prompts into tasks
  - **Scraper**: Fetches content from URLs (PyTorch news by default)
  - **FileWriter**: Persists generated content
  - **Scheduler**: Monitors approval responses
- **Network**: All services share `supervisor_net` Docker network
- **Logging**: Persistent logs in `./logs` directory

## File Structure

```
.
├── deploy.sh                 # Deployment script
├── docker-compose.full.yml   # Docker Compose configuration
├── main.py                   # FastAPI backend
├── bot.py                    # Telegram bot
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── .dockerignore              # Docker build exclusions
├── README.md                 # This file
└── agents/
    ├── __init__.py
    ├── models.py             # Pydantic data models
    ├── utils.py              # Logging utilities
    ├── planner.py            # PlannerAgent class
    ├── scraper.py            # ScraperAgent class
    ├── file_writer.py        # FileWriterAgent class
    └── scheduler.py          # SchedulerAgent class
```

## Notes

- If running on a different host, update `BACKEND_API_URL` accordingly
- All services automatically restart unless explicitly stopped
- Health checks run every 30 seconds on the `/health` endpoint
- Logs are persisted in the mounted `./logs` directory
