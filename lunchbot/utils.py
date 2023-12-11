import logging


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)

    # Create a formatter that includes the logger name, time, log level, and message
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # Create a handler that outputs to the console, and set its formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Set the log level
    logger.setLevel(level)

    return logger
