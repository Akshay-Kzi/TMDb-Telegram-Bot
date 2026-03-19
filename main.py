import logging
import os
from dotenv import load_dotenv
from app.tmdb import search_movie, get_movie_details, normalize_movie
from app.template_engine import render_template

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
        try:
            details = get_movie_details(movie["id"])
            data = normalize_movie(details)
        except Exception as e:
            print(f"Error fetching details for movie {movie['id']}: {e}")
            continue

        template = context.bot_data.get(
            "default_template",
            "<b>#TITLE</b> (#YEAR)\n⭐ #RATING"
        )

        rendered = render_template(template, data)

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{data['title'] or 'Unknown Title'} ({data['year'] or 'Unknown Year'})",
                description=(data["plot"] or "No description available")[:300],
                input_message_content=InputTextMessageContent(
                    message_text=rendered,
                    parse_mode="HTML",
                    disable_web_page_preview=False
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
