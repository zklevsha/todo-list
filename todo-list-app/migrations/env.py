from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from models import Base
from settings import connection_string, test_connection_string

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option('sqlalchemy.url', connection_string)

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable_main = create_async_engine(
        connection_string,
        future=True,
        poolclass=pool.NullPool,
    )
    connectable_test = create_async_engine(
        test_connection_string,
        future=True,
        poolclass=pool.NullPool,
    )

    for connectable in [connectable_main, connectable_test]:
        try:
            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)
        except Exception as e:
            print(f"Failed to run migrations for {connectable.url}: {e}")
        finally:
            await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
