import logging
import os
from dotenv import load_dotenv
from app.tmdb import search_movie, get_movie_details, normalize_movie
from app.template_engine import render_template
from app.database import get_or_create_user, update_user_usage, is_superuser, grant_superuser, revoke_superuser, get_all_users

load_dotenv()

from telegram import InlineQueryResultPhoto, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes, CommandHandler
from telegram.error import BadRequest
import uuid

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

async def start_command(update, context):
    """Handle /start command with welcome message and inline button"""
    welcome_message = """
🎬 **Welcome to MovieBot!**

I'm your personal movie assistant powered by TMDb. 

🔍 **How to use:**
- Type the username of bot followed by movie title (For example: `@TMDbInfoKziBot inception`) in any chat
- Or click the button below to search inline

📊 **Features:**
- Detailed movie information
- Poster images
- Cast, crew, and ratings
- Fast response with caching

Made with ❤️ using Python and TMDb API
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search Movies", switch_inline_query="")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)


async def grant_command(update, context):
    """Grant superuser access to a user (superuser only)"""
    user_id = update.effective_user.id
    
    if not is_superuser(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /grant <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        grant_superuser(target_id)
        await update.message.reply_text(f"✅ Superuser access granted to {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")


async def revoke_command(update, context):
    """Revoke superuser access from a user (superuser only)"""
    user_id = update.effective_user.id
    
    if not is_superuser(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /revoke <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        revoke_superuser(target_id)
        await update.message.reply_text(f"✅ Superuser access revoked from {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")


async def stats_command(update, context):
    """Show usage statistics (superuser only)"""
    user_id = update.effective_user.id
    
    if not is_superuser(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("No users found.")
        return
    
    stats_text = "📊 User Statistics\n\n"
    for user in users[:20]:  # Show top 20 users
        superuser_badge = "⭐ " if user['is_superuser'] else ""
        username = user['username'] or "Unknown"
        # Escape special characters for Markdown
        username = username.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
        stats_text += f"{superuser_badge}{username} (ID: {user['id']})\n"
        stats_text += f"   Queries: {user['query_count']}\n\n"
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")


async def inline_query_handler(update, context):
    query = update.inline_query.query.strip()

    if not query:
        return

    # Track user usage
    user_id = update.inline_query.from_user.id
    username = update.inline_query.from_user.username
    get_or_create_user(user_id, username)
    update_user_usage(user_id)

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
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("grant", grant_command))
    app.add_handler(CommandHandler("revoke", revoke_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
