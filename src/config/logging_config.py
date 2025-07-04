import logging
import os
from config.settings import LOG_LEVEL, LOG_FILE

def setup_logging():
    """
    Sets up basic logging for the application.
    Logs will be written to a file and to the console.
    """
    # Ensure the log directory exists
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    # Create a logger
    logger = logging.getLogger('severino')
    logger.setLevel(LOG_LEVEL)

    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Initialize logger when this module is imported
logger = setup_logging()

if __name__ == "__main__":
    # Example usage if this script is run directly
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
