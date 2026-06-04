import logging
import sys

_LOG_CONFIGURED = False


def setup_logging(level=logging.INFO):
    """Configure logging once. Safe to call multiple times."""
    global _LOG_CONFIGURED
    if _LOG_CONFIGURED:
        return
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    _LOG_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name."""
    setup_logging()
    return logging.getLogger(name)
