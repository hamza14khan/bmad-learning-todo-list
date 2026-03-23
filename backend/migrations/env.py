"""
Alembic environment configuration.

This file is run by Alembic when generating or applying migrations.
Key customisations from the default:
- Loads DATABASE_URL from .env file
- Imports our models so Alembic can detect schema changes (autogenerate)
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Add backend/ to sys.path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env before importing models (database.py needs DATABASE_URL)
load_dotenv()

# Import Base and models — Alembic needs these to detect table changes
from database import Base  # noqa: E402
import models  # noqa: E402, F401 — F401 suppressed: import needed for autogenerate

# Alembic Config object — gives access to alembic.ini values
config = context.config

# Override the sqlalchemy.url from alembic.ini with our env var
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Set up Python logging from alembic.ini config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic which metadata to compare against (our models)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations without a live database connection.
    Used for generating SQL scripts.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations with a live database connection.
    Used for `alembic upgrade head` — the normal workflow.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
