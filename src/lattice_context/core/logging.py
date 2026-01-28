"""Structured logging configuration for Lattice."""

import logging
import sys

import structlog


def configure_logging(verbose: bool = False) -> None:
    """Configure structured logging."""

    # Set log level based on verbosity
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer() if verbose else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)
