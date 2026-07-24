#!/usr/bin/env python3
import asyncio
import logging
import os
import json
from typing import Dict, Any

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def send_to_backend(user_id: int, prompt: str) -> Dict[str, Any]:
    payload = {
        "user_id": user_id,
        "prompt": prompt
    }
    
    timeout = aiohttp.ClientTimeout(total=120)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                f"{BACKEND_API_URL}/process_request",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "success", "data": data}
                else:
                    error_text = await response.text()
                    return {
                        "status": "error", 
                        "message": f"Backend returned status {response.status}: {error_text}"
                    }
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Backend request timed out after 120 seconds"}
        except aiohttp.ClientError as e:
            return {"status": "error", "message": f"Backend unreachable: {str(e)}"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON response from backend"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "👋 Welcome! I'm your AI Assistant Bot.\n\n"
        "I forward your messages to an AI Supervisor backend.\n\n"
        "Send me any message and I'll process it through the AI system!"
    )
    await update.message.reply_text(welcome_message)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"Received message from user {user.id}: {message_text[:50]}...")
    
    backend_response = await send_to_backend(user.id, message_text)
    
    try:
        if backend_response.get("data", {}).get("status") == "awaiting_approval":
            data = backend_response["data"]["data"]
            plan_summary = data.get("plan_summary", "No plan summary available")
            plan_id = data.get("plan_id", str(user.id))
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve & Deploy", callback_data=f"approve_{plan_id}"),
                    InlineKeyboardButton("✏️ Modify", callback_data=f"modify_{plan_id}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Archive", callback_data=f"archive_{plan_id}")
                ]
            ])
            
            response_message = (
                f"📋 **Plan Awaiting Approval**\n\n"
                f"📝 **Summary:** {plan_summary}\n\n"
                f"Choose an action below:"
            )
            
            if not context.user_data:
                context.user_data[user.id] = {}
            context.user_data[user.id]["current_plan_id"] = plan_id
            
            await update.message.reply_text(
                response_message, 
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        else:
            message_text = backend_response.get("data", {}).get("message", "No response from backend")
            await update.message.reply_text(message_text)
            
    except Exception as e:
        logger.error(f"Error processing backend response: {str(e)}")
        await update.message.reply_text("Error processing backend response. Please try again.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    logger.info(f"Callback query from user {user_id}: {callback_data}")
    
    user_data = context.user_data.get(user_id, {})
    plan_id = user_data.get("current_plan_id")
    
    try:
        if callback_data.startswith("approve_"):
            callback_plan_id = callback_data.split("_")[1]
            actual_plan_id = callback_plan_id if callback_plan_id else plan_id
            
            if not actual_plan_id:
                await query.answer("Error: No plan ID found", show_alert=True)
                return
            
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f"{BACKEND_API_URL}/approve_plan",
                    json={"plan_id": actual_plan_id, "user_id": user_id},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status == 200:
                    await query.answer("Plan approved and deployed! ✅", show_alert=True)
                    await query.edit_message_text(
                        "✅ Plan approved and deployed successfully!",
                        reply_markup=None
                    )
                else:
                    error_text = await response.text()
                    await query.answer(f"Approval failed: {error_text}", show_alert=True)
                    
        elif callback_data.startswith("modify_"):
            callback_plan_id = callback_data.split("_")[1]
            actual_plan_id = callback_plan_id if callback_plan_id else plan_id
            
            await query.answer("Modification interface opened", show_alert=True)
            await query.edit_message_text(
                f"✏️ Modification not yet implemented for plan {actual_plan_id}.",
                reply_markup=None
            )
            context.user_data[user_id]["awaiting_modification"] = actual_plan_id
            
        elif callback_data.startswith("archive_"):
            callback_plan_id = callback_data.split("_")[1]
            actual_plan_id = callback_plan_id if callback_plan_id else plan_id
            
            await query.answer("Plan archived! 🗑️", show_alert=True)
            await query.edit_message_text(
                "🗑️ Plan archived successfully.",
                reply_markup=None
            )
            
    except Exception as e:
        logger.error(f"Error handling callback query {callback_data}: {str(e)}")
        await query.answer("Error processing your request", show_alert=True)
        
    if user_id in context.user_data:
        context.user_data[user_id].pop("current_plan_id", None)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again later."
        )

async def main() -> None:
    logger.info("Starting Telegram bot...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_error_handler(error_handler)
    
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
