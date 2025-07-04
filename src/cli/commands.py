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

@cli.command()
@click.option('--model', type=click.Choice(['gemma', 'gemini'], case_sensitive=False), default='gemini',
              help='Choose the LLM model for the chat session (gemma or gemini).')
@click.option('--max-tokens', default=512, type=int,
              help='Maximum number of tokens for model generation in chat.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the Gemma model (0.0-1.0). Higher values are more creative.')
def chat(model: str, max_tokens: int, temperature: float):
    """
    Starts an interactive chat session with the chosen LLM.
    Type 'exit' or 'quit' to end the session.
    """
    logger.info(f"Starting interactive chat session with {model} model.")
    print(f"Starting interactive chat with {model}. Type 'exit' or 'quit' to end.")

    chat_history = []
    gemini_chat_session = None

    if model == 'gemini':
        from llm_inference.gemini_api import start_gemini_chat_session
        gemini_chat_session = start_gemini_chat_session()
        print("Gemini chat session started.")
    elif model == 'gemma':
        try:
            load_gemma_model() # Ensure Gemma model is loaded once
            print("Gemma model loaded for chat.")
        except FileNotFoundError as e:
            print(f"\nError: {e}")
            print("Please ensure the Gemma GGUF model is downloaded to 'data/models/'. Cannot start Gemma chat.")
            logger.error(f"Gemma chat failed: Model file not found. {e}")
            return
        except Exception as e:
            print(f"\nAn unexpected error occurred during Gemma model loading: {e}")
            logger.error(f"Gemma chat failed unexpectedly during model loading: {e}", exc_info=True)
            return

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Ending chat session.")
                logger.info("Chat session ended by user.")
                break

            if not user_input:
                continue

            response = None
            if model == 'gemini':
                response = generate_content_with_quota_check(
                    user_input,
                    max_tokens=max_tokens,
                    chat_session=gemini_chat_session
                )
            elif model == 'gemma':
                response = run_gemma_inference(
                    user_input,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    chat_history=chat_history # Pass history for Gemma
                )
            
            if response:
                print(f"\n{model.capitalize()}: {response}")
                # Add both user input and model response to history for Gemma
                if model == 'gemma':
                    chat_history.append(f"<start_of_turn>user\n{user_input}<end_of_turn>\n<start_of_turn>model\n{response}<end_of_turn>")
            else:
                print(f"No response from {model}.")

        except KeyboardInterrupt:
            print("\nEnding chat session.")
            logger.info("Chat session ended by KeyboardInterrupt.")
            break
        except Exception as e:
            print(f"\nAn error occurred during chat: {e}")
            logger.error(f"Chat session error: {e}", exc_info=True)

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
