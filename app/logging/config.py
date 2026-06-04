import os
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from app.logging.middleware import request_id_var


LOG_DIR = Path("logs")


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _record_enricher(record: Dict[str, Any]) -> None:
    request_id = request_id_var.get()
    record["extra"]["request_id"] = request_id


def configure_logging() -> None:
    """
    Configure Loguru logging only once.
    Creates log directory and sets up sinks.
    """

    if getattr(configure_logging, "_configured", False):
        return

    _ensure_log_dir()

    # Remove default logger
    logger.remove()

    # Configure sinks
    _configure_sinks()

    # Add request_id to every log record
    logger.configure(patcher=_record_enricher)

    configure_logging._configured = True  # type: ignore[attr-defined]


def _configure_sinks() -> None:
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level}</level> | "
        "request_id={extra[request_id]} | "
        "{module}:{function}:{line} - "
        "<level>{message}</level>"
    )

    logger.add(
        os.fspath(LOG_DIR / "app.log"),
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=log_format,
    )

    logger.add(
        os.fspath(LOG_DIR / "api.log"),
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=log_format,
    )

    logger.add(
        os.fspath(LOG_DIR / "llm.log"),
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=log_format,
        filter=lambda record: record["extra"].get("channel") == "llm",
    )

    logger.add(
        os.fspath(LOG_DIR / "error.log"),
        level="ERROR",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=log_format,
    )


