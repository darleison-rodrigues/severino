import click
from cli.commands import cli
from config.logging_config import logger

# The main entry point for the Severino CLI application.
# It uses the 'click' library to define and manage command-line commands.

if __name__ == '__main__':
    # Initialize logging for the application.
    # This will ensure logs are written to file and console as configured.
    logger.info("Severino CLI started.")
    try:
        # Call the main CLI group defined in src.cli.commands.
        # Click handles parsing arguments and dispatching to the correct command function.
        cli()
    except Exception as e:
        logger.critical(f"An unhandled critical error occurred: {e}", exc_info=True)
        print("\n[bold red]A critical error occurred. Please check the logs for details.[/bold red]")