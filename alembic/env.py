from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
from setting import Engine, Base
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# Set target metadata for 'autogenerate' support.
target_metadata = Base.metadata  # setting.pyのBaseを使う

def run_migrations_offline():
    url = os.getenv("HIMAZIN_DATABASE_URL")  # 環境変数からURL取得
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = Engine  # setting.pyのEngineを使用

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()