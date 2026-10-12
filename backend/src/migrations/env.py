import os

from apex_ai.database.base import Base
from apex_ai.database import models

config.set_main_option(
    "sqlalchemy.url",
    os.environ["DATABASE_URL"].replace("%", "%%"),
)

target_metadata = Base.metadata