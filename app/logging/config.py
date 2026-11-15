import os
from pathlib import Path
from typing import Any

from loguru import logger

from app.logging.middleware import request_id_var

LOG_DIR = Path("logs")


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _record_enricher(record: dict[str, Any]) -> None:
    request_id = request_id_var.get()
    record["extra"]["request_id"] = request_id


def configure_logging() -> None:
    if getattr(configure_logging, "_configured", False):
        return

    _ensure_log_dir()
    logger.remove()
    _configure_sinks()
    logger.configure(patcher=_record_enricher)

    configure_logging._configured = True  # type: ignore[attr-defined]


def _configure_sinks():
    from loguru import logger as _logger

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level}</level> | "
        "request_id={extra[request_id]} | "
        "{module}:{function}:{line} - "
        "<level>{message}</level>"
    )

    _logger.add(
        os.fspath(LOG_DIR / "app.log"),
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=log_format,
    )

    _logger.add(
        os.fspath(LOG_DIR / "api.log"),
        level="INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=log_format,
    )

    _logger.add(
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

    _logger.add(
        os.fspath(LOG_DIR / "error.log"),
        level="ERROR",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=log_format,
    )

    return _logger
