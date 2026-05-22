"""Logger setup using loguru."""
import os
import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_path: str = None, level: str = "INFO"):
    """Configure loguru logger with console + file output."""
    logger.remove()  # Remove default handler

    # Console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
               "<level>{message}</level>",
        level=level,
        colorize=True,
    )

    # File handler
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                   "{name}:{function}:{line} - {message}",
        )

    return logger


def get_logger():
    """Get configured logger instance."""
    return logger
