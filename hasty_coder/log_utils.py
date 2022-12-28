import logging.config


def configure_logging(level="INFO"):
    """Configure logging with optional level parameter."""
    fmt = "%(message)s"
    if level == "DEBUG":
        fmt = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "simple": {
                "format": fmt,
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "simple",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
            "hasty_coder": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
