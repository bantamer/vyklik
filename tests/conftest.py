import os

# Tests must not require a real .env file or a real bot token.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("POSTGRES_DSN", "postgresql+asyncpg://test:test@localhost/test")
