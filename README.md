# 🎬 TMDb Telegram Bot

A feature-rich Telegram inline bot for searching movies using the TMDb API. Get detailed movie information, poster images, cast/crew details, and more - all with fast response times thanks to intelligent caching.

## ✨ Features

- **Inline Search**: Search movies directly in any Telegram chat using inline query (e.g., `@TMDbInfoKziBot inception`)
- **Detailed Information**: Title, year, genres, rating, languages, directors, writers, cast, duration, and plot
- **Poster Images**: High-quality movie posters displayed inline
- **Smart Caching**: SQLite-based caching system for lightning-fast responses
- **User Tracking**: Track usage statistics and manage user access
- **Superuser System**: Grant/revoke access and view usage statistics
- **Custom Templates**: Support for custom output templates (planned)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- TMDb API Key from [TMDb](https://www.themoviedb.org/settings/api)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akshay-Kzi/TMDb-Telegram-Bot.git
   cd TMDb-Telegram-Bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\Activate.ps1
   # On Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   TMDB_API_KEY=your_tmdb_api_key_here
   OWNER_ID=your_telegram_user_id
   DATABASE_PATH=bot.db
   PUBLIC_MODE=True
   ```

5. **Set up the main superuser**
   
   The bot will automatically create the main superuser when you first run it. To set a specific superuser ID, run:
   ```bash
   python -c "from app.database import get_or_create_user, grant_superuser; get_or_create_user(1609185280, 'main_superuser'); grant_superuser(1609185280); print('Superuser set')"
   ```
   
   Replace `1609185280` with your Telegram user ID.

6. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TMDB_API_KEY` | Your TMDb API key | `abcdef1234567890abcdef1234567890` |
| `OWNER_ID` | Your Telegram user ID (for owner access) | `1609185280` |
| `DATABASE_PATH` | Path to SQLite database file | `bot.db` |
| `PUBLIC_MODE` | Allow public access to the bot | `True` |

### Getting Your Telegram User ID

1. Start a chat with [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. The bot will reply with your user ID

### Getting TMDb API Key

1. Go to [TMDb Settings](https://www.themoviedb.org/settings/api)
2. Sign in or create an account
3. Click "Create" under "API Key"
4. Fill in the required information
5. Copy your API key

## 📖 Usage

### Inline Search

Type `@YourBotName movie_name` in any Telegram chat to search for movies. The bot will show results with detailed information including:

- Movie poster
- Title and year
- Genres
- Rating and vote count
- Languages
- Directors, writers, and cast
- Duration
- Plot summary

### Bot Commands

- `/start` - Welcome message with search button
- Only superusers can use these commands:
  - `/grant <user_id>` - Grant superuser access (superuser only)
  - `/revoke <user_id>` - Revoke superuser access (superuser only)
  - `/stats` - View user statistics (superuser only)


## 🗄️ Database

The bot uses SQLite for:

- **User Management**: Track users, query counts, and superuser status
- **Caching**: Store TMDb API responses to reduce API calls and improve speed
- **Templates**: Store custom user templates (planned feature)

### Cache Configuration

- **Search results**: Cached for 1 hour
- **Movie details**: Cached for 24 hours
- **Automatic cleanup**: Expired entries are removed on access

## 🛠️ Development

### Project Structure

```
moviebot/
├── main.py                 # Bot entry point and command handlers
├── app/
│   ├── config.py          # Configuration loading
│   ├── database.py        # Database operations and caching
│   ├── template_engine.py # Template rendering system
│   └── tmdb.py            # TMDb API integration
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Running Tests

```bash
# Test cache system
python -c "from app.tmdb import search_movie; search_movie('inception')"

# Test database
python -c "from app.database import init_db; init_db()"

# Check user stats
python -c "from app.database import get_all_users; print(get_all_users())"
```

## 🌐 Deployment

### Oracle Cloud Free Tier

1. **Create an Oracle Cloud Free Tier account**
   - Sign up at [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
   - You get 2 AMD-based VMs with 1/8 OCPU and 1 GB RAM each

2. **Create a VM instance**
   - Go to Compute → Instances → Create Instance
   - Choose: Oracle Linux, AMD, 1 OCPU, 1 GB RAM
   - Add SSH public key for access

3. **Connect to your VM**
   ```bash
   ssh -i your_key.pem opc@your_vm_ip
   ```

4. **Install Python and dependencies**
   ```bash
   sudo yum install python3 python3-pip git
   ```

5. **Clone the repository**
   ```bash
   git clone https://github.com/Akshay-Kzi/TMDb-Telegram-Bot.git
   cd TMDb-Telegram-Bot
   ```

6. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

7. **Configure environment variables**
   ```bash
   nano .env
   # Add your BOT_TOKEN, TMDB_API_KEY, etc.
   ```

8. **Run the bot with systemd**
   
   Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/moviebot.service
   ```
   
   Add this content:
   ```ini
   [Unit]
   Description=TMDb Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=opc
   WorkingDirectory=/home/opc/TMDb-Telegram-Bot
   Environment="PATH=/home/opc/TMDb-Telegram-Bot/.venv/bin"
   ExecStart=/home/opc/TMDb-Telegram-Bot/.venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   
   Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start moviebot
   sudo systemctl enable moviebot
   ```

9. **Check logs**
   ```bash
   sudo journalctl -u moviebot -f
   ```

### Other Deployment Options

- **Heroku**: Use a worker dyno with the Procfile
- **Railway**: Simple deployment with automatic builds
- **VPS**: Any VPS provider (DigitalOcean, Linode, etc.)
- **Docker**: Create a Dockerfile for containerized deployment

## 🔒 Security

- **Never commit** `.env` file or `bot.db` to version control
- **Keep your API keys secret** and rotate them regularly
- **Use strong passwords** for database encryption (if implemented)
- **Limit superuser access** to trusted individuals only
- **Monitor usage** with the `/stats` command

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Bot not responding
- Check if the bot token is correct
- Ensure the bot is running (`python main.py`)
- Check Telegram logs for errors

### Timeout errors
- The bot uses caching to prevent timeouts
- If timeouts persist, check your internet connection
- Reduce the number of movies returned (currently set to 1)

### Database errors
- Ensure `bot.db` is writable
- Check that SQLite is installed
- Try deleting `bot.db` and letting the bot recreate it

### API errors
- Verify your TMDb API key is valid
- Check if you've exceeded TMDb API rate limits
- Ensure your API key has the correct permissions

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the maintainer

## 🙏 Acknowledgments

- [TMDb](https://www.themoviedb.org/) for the movie database API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram bot framework
- All contributors and users of this bot

---

Yeah, this is vibe coded ofc
