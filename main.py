import logging
import os
from dotenv import load_dotenv
from app.tmdb import search_movie, get_movie_details

load_dotenv()

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
import uuid

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

async def inline_query_handler(update, context):
    query = update.inline_query.query.strip()

    if not query:
        return

    try:
        movies = search_movie(query)[:5]
    except Exception as e:
        print("TMDb error:", e)
        return

    results = []

    for movie in movies:
        title = movie.get("title", "Unknown")
        year = (movie.get("release_date") or "")[:4]
        overview = movie.get("overview", "")[:300]

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{title} ({year})",
                description=overview,
                input_message_content=InputTextMessageContent(
                    message_text="Fetching details...",
                    parse_mode="HTML"
                )
            )
        )

    await update.inline_query.answer(results, cache_time=1)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
