import logging
import os
from dotenv import load_dotenv

load_dotenv()

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

async def inline_query_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()

    if not query:
        return

    results = [
        InlineQueryResultArticle(
            id="test-1",
            title="Dummy Movie Result",
            description=f"You searched: {query}",
            input_message_content=InputTextMessageContent(
                message_text=f"<b>Inline bot working</b>\nQuery: {query}",
                parse_mode="HTML",
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=1)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
