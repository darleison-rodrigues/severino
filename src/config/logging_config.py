import logging
import os
from rich.logging import RichHandler
from rich.console import Console
from config.settings import LOG_LEVEL, LOG_FILE

def setup_logging():
    """
    Sets up basic logging for the application with Rich for console output.
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

        # Console handler with Rich
        console = Console()
        rich_handler = RichHandler(
            level=LOG_LEVEL,
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            enable_link_path=False,
            markup=True,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
            keywords=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] # Highlight log levels
        )
        
        # Custom format for RichHandler to include nerdy emojis
        # Note: RichHandler formats messages internally, so we'll use extra for emojis
        # and let Rich handle the rest of the formatting.
        # The emojis will be prepended in the actual log calls.
        
        logger.addHandler(rich_handler)

    return logger

# Initialize logger when this module is imported
logger = setup_logging()

if __name__ == "__main__":
    # Example usage if this script is run directly
    logger.debug("🐛 [bold blue]Debugging[/bold blue] a cosmic ray... This is a debug message.")
    logger.info("💡 [bold green]Insight[/bold green] unlocked! This is an info message.")
    logger.warning("⚠️ [bold yellow]Anomaly[/bold yellow] detected! This is a warning message.")
    logger.error("🔥 [bold red]Critical failure[/bold red]! This is an error message.")
    logger.critical("💀 [bold magenta]System meltdown[/bold magenta]! This is a critical message.")

