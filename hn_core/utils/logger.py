import logging


def get_logger(name: str) -> logging.Logger:
    """Factory for creating logger instance"""
    logger = logging.getLogger(name)
    # Only add handler if the logger doesn't already have one
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
