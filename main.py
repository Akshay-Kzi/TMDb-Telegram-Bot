import logging
import os
from dotenv import load_dotenv
from app.tmdb import search_movie, get_movie_details, normalize_movie
from app.template_engine import render_template

load_dotenv()

from telegram import InlineQueryResultPhoto, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
from telegram.error import BadRequest
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
        movies = search_movie(query)[:1]  # Just 1 movie to prevent timeouts
    except Exception as e:
        print("TMDb error:", e)
        return

    results = []

    for movie in movies:
        try:
            # Get detailed information for better formatting
            details = get_movie_details(movie["id"])
            data = normalize_movie(details)
        except Exception as e:
            print(f"Error fetching details for movie {movie['id']}: {e}")
            # Fallback to search data if details fail
            data = {
                "title": movie.get("title"),
                "year": (movie.get("release_date") or "")[:4],
                "rating": movie.get("vote_average"),
                "votes": movie.get("vote_count"),
                "runtime": None,
                "duration_format": "N/A",
                "genres": "",
                "plot": movie.get("overview"),
                "poster": (
                    f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                    if movie.get("poster_path") else None
                ),
                "language": "",
                "director": "",
                "writer": "",
                "cast": "",
                "country": "",
            }

        template = context.bot_data.get(
            "default_template",
            """🏷 Title: #TITLE
🎭 Genres: #GENRE
📆 Year: #YEAR
🌟 Rating: #RATING / 10  ( based on #VOTES user ratings )
☀️ Languages :  #LANGUAGE
👥 
Directors  #DIRECTOR
Writers  #WRITER
Stars  #CAST

📀 Duration : #DURATION_FORMAT
🎛 Country Of Origin :  #COUNTRY
🔰Story Line : #STORY_LINE"""
        )

        rendered = render_template(template, data)

        poster_url = data.get("poster") or "https://via.placeholder.com/300x450?text=No+Image"

        results.append(
            InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=poster_url,
                thumbnail_url=poster_url,
                title=f"{data['title'] or 'Unknown Title'} ({data['year'] or 'Unknown Year'})",
                description=(data["plot"] or "No description available")[:300],
                caption=rendered,
                parse_mode="HTML"
            )
        )


    try:
        await update.inline_query.answer(results, cache_time=1)
    except BadRequest as e:
        if "too old" in str(e).lower() or "timeout" in str(e).lower():
            logging.warning(f"Inline query timeout: {e}")
        else:
            logging.error(f"BadRequest error: {e}")
    except Exception as e:
        logging.error(f"Error answering inline query: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
