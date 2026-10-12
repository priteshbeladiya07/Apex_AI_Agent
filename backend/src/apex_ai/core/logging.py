import logging

from apex_ai.core.config import settings


def configure_logging() -> None:
    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)

    if not isinstance(level, int):
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"apex_ai.{name}")