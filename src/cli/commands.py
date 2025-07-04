import click
from llm_inference.gemma_local import run_gemma_inference, load_gemma_model
from llm_inference.gemini_api import generate_content_with_quota_check
from config.settings import MAX_GEMINI_OUTPUT_TOKENS
from config.logging_config import logger
import os

# The main CLI group for the Severino application.
# All commands will be registered under this group.
@click.group()
def cli():
    """
    Severino: A CLI for ML monitoring assistance using Gemma and Gemini.
    Use 'severino <command> --help' for more information on each command.
    """
    pass # No specific initialization needed for the main group itself

@cli.command()
@click.argument('prompt')
@click.option('--max-tokens', default=256, type=int,
              help='Maximum number of tokens to generate locally by Gemma.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the Gemma model (0.0-1.0). Higher values are more creative.')
def gemma(prompt: str, max_tokens: int, temperature: float):
    """
    Runs local inference using the Gemma model.
    Ideal for quick insights, coding help, or general tasks where speed and privacy are key.
    Requires a Gemma GGUF model to be downloaded in 'data/models/'.
    """
    logger.info(f"Executing 'gemma' command with prompt: '{prompt}'")
    print(f"Running Gemma locally for: '{prompt}'")

    try:
        # Attempt to load the Gemma model. This will raise an error if the model isn't found.
        # The model is loaded once and reused across subsequent 'gemma' calls.
        load_gemma_model()
        response = run_gemma_inference(prompt, max_tokens, temperature)
        print("\n--- Gemma Response ---")
        print(response)
        logger.info("Gemma command completed successfully.")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please ensure the Gemma GGUF model is downloaded to 'data/models/'.")
        logger.error(f"Gemma command failed: Model file not found. {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during Gemma inference: {e}")
        logger.error(f"Gemma command failed unexpectedly: {e}", exc_info=True)



@cli.command()
@click.argument('prompt')
@click.option('--max-tokens', default=MAX_GEMINI_OUTPUT_TOKENS, type=int,
              help=f'Maximum number of tokens for Gemini API generation (default: {MAX_GEMINI_OUTPUT_TOKENS}).')
def gemini(prompt: str, max_tokens: int):
    """
    Generates content using the Gemini API.
    Best for high-quality, complex, or longer responses.
    Note: Usage of the Gemini API may incur charges based on Google Cloud billing.
    """
    logger.info(f"Executing 'gemini' command with prompt: '{prompt}'")
    click.echo(f"Requesting Gemini API for: '{prompt}'")

    response = generate_content_with_quota_check(prompt, max_tokens)
    if response:
        click.echo("\n--- Gemini API Response ---")
        click.echo(response)
        logger.info("Gemini command completed successfully.")
    else:
        click.echo("Gemini API request failed or was cancelled.")
        logger.warning("Gemini command did not return a response.")

# You can add more commands here as your CLI grows, for example:
# @cli.command()
# @click.argument('log_file', type=click.Path(exists=True))
# def analyze_logs(log_file: str):
#     """
#     Analyzes an ML model log file using LLMs to identify issues.
#     (Conceptual: would involve reading logs and passing to Gemma/Gemini)
#     """
#     logger.info(f"Analyzing log file: {log_file}")
#     click.echo(f"Analyzing {log_file} for insights...")
#     # Example: Read log content, then use an LLM to summarize/identify issues
#     # with open(log_file, 'r') as f:
#     #     log_content = f.read()
#     #
#     # # Use Gemma for quick summary, or Gemini for deeper analysis
#     # summary_prompt = f"Summarize key errors or anomalies from this log: {log_content[:2000]}..."
#     # summary = run_gemma_inference(summary_prompt, max_tokens=500)
#     # click.echo(f"\n--- Log Summary ---\n{summary}")
#     logger.info("Log analysis command executed (conceptual).")

# @cli.command()
# @click.option('--report-type', type=click.Choice(['daily', 'weekly', 'monthly']), default='daily',
#               help='Type of report to generate.')
# def generate_report(report_type: str):
#     """
#     Generates a performance report based on collected data.
#     (Conceptual: would involve data retrieval and Gemini API for structured report generation)
#     """
#     logger.info(f"Generating {report_type} report.")
#     click.echo(f"Generating a {report_type} performance report...")
#     # Example: Retrieve data from cache/database, then use Gemini to format a report
#     # data_for_report = retrieve_data(report_type)
#     # report_prompt = f"Generate a {report_type} performance report based on this data: {data_for_report}"
#     # report = generate_content_with_quota_check(report_prompt, max_tokens=2000)
#     # if report:
#     #     click.echo(f"\n--- Generated Report ---\n{report}")
#     logger.info("Report generation command executed (conceptual).")
