# Simple deployment for Render

You can deploy this project to Render using the button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=captainduallysamazingstuff-ops/Sup)

## Manual Setup on Render

### 1. Go to Render Dashboard
https://dashboard.render.com

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repo: `captainduallysamazingstuff-ops/Sup`
- Name: `supervisor-backend`
- Runtime: `Docker`
- Plan: `Free`
- Branch: `main`
- Click "Create Web Service"

### 3. Add Environment Variables
In the "Environment" section, add:
```
APP_NAME=TelegramBotBackend
DEBUG=false
```

### 4. Wait for Deployment
Render will build and deploy automatically. Copy your service URL (looks like `https://supervisor-backend-xxxxx.onrender.com`)

### 5. Create Background Service for Bot
- Click "New +" → "Background Worker"
- Connect same repo
- Name: `telegram-bot`
- Runtime: `Docker`
- Build Command: (leave empty)
- Start Command: `python bot.py`
- Plan: `Free`

### 6. Add Bot Environment Variables
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
BACKEND_API_URL=https://supervisor-backend-xxxxx.onrender.com
```
(Replace with your actual backend URL from step 4)

### 7. Deploy Bot Service
Click "Create Background Worker"

## That's it!
Your bot should now be running on Render. Find it on Telegram and send `/start`!
