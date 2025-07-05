import click
from llm_inference.gemma_local import run_gemma_inference, load_gemma_model
from llm_inference.gemini_api import generate_content_with_quota_check
from config.settings import MAX_GEMINI_OUTPUT_TOKENS
from config.logging_config import logger
import os
from rich.console import Console
from rich.status import Status
from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
import time

from packages.core.state_manager import StateManager

console = Console()
state_manager = StateManager(session_id="cli_session") # Using a fixed session ID for CLI

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
    console.print(f"[bold blue]Running Gemma locally for:[/bold blue] '{prompt}'")

    try:
        # Attempt to load the Gemma model. This will raise an error if the model isn't found.
        # The model is loaded once and reused across subsequent 'gemma' calls.
        load_gemma_model()
        response = run_gemma_inference(prompt, max_tokens, temperature)
        console.print("\n[bold green]--- Gemma Response ---\/bold green]")
        console.print(response)
        
    except FileNotFoundError as e:
        console.print(f"
[bold red]Error: {e}[/bold red]")
        console.print("[bold red]Please ensure the Gemma GGUF model is downloaded to 'data/models/'.[/bold red]")
        
    except Exception as e:
        console.print(f"
[bold red]An unexpected error occurred during Gemma inference: {e}[/bold red]")
        



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
    console.print(f"[bold blue]Requesting Gemini API for:[/bold blue] '{prompt}'")

    response = generate_content_with_quota_check(prompt, max_tokens)
    if response:
        console.print("\n[bold green]--- Gemini API Response ---[/bold green]")
        console.print(response)
    else:
        console.print("[bold red]Gemini API request failed or was cancelled.[/bold red]")

@cli.command()
@click.option('--model', type=click.Choice(['gemma', 'gemini'], case_sensitive=False), default='gemma',
              help='Choose the LLM model for the chat session (gemma or gemini).')
@click.option('--max-tokens', default=512, type=int,
              help='Maximum number of tokens for model generation in chat.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the Gemma model (0.0-1.0). Higher values are more creative.')
def chat(model: str, max_tokens: int, temperature: float):
    """
    Starts an interactive chat session with the chosen LLM.
    Type 'exit' or 'quit' to end the session.
    Use '/use gemini' to enable Gemini API for the session.
    """
    
    console.print(f"[bold green]Starting interactive chat with {model.capitalize()}.[/bold green] Type '[bold red]exit[/bold red]' or '[bold red]quit[/bold red]' to end.")
    console.print("[bold yellow]Use '/use gemini' to enable Gemini API for this session.[/bold yellow]")

    chat_history = []
    gemini_chat_session = None
    
    # Initialize gemini_authorized state
    state_manager.update_session_data("gemini_authorized", False)

    if model == 'gemma':
        try:
            load_gemma_model() # Ensure Gemma model is loaded once
            console.print("[green]Gemma model loaded for chat.[/green]")
        except FileNotFoundError as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            console.print("[bold red]Please ensure the Gemma GGUF model is downloaded to 'data/models/'. Cannot start Gemma chat.[/bold red]")
            return
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred during Gemma model loading: {e}[/bold red]")
            return
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if user_input.lower() == '/use gemini':
                state_manager.update_session_data("gemini_authorized", True)
                console.print("[bold yellow]Gemini API is now [green]ENABLED[/green] for this session.[/bold yellow]")
                continue

            if not user_input:
                continue

            response = None
            current_model = model
            
            # Check if Gemini is authorized and switch model if requested implicitly or explicitly
            if state_manager.get_session_data("gemini_authorized") and model == 'gemini': # If model was explicitly set to gemini
                current_model = 'gemini'
            elif state_manager.get_session_data("gemini_authorized") and user_input.lower().startswith('/gemini '):
                current_model = 'gemini'
                user_input = user_input[len('/gemini '):].strip() # Remove command prefix
            elif not state_manager.get_session_data("gemini_authorized") and model == 'gemini':
                console.print("[bold red]Gemini API is not authorized for this session. Use '/use gemini' to enable it.[/bold red]")
                continue

            with Status("[bold yellow]Thinking...[/bold yellow]", spinner="dots", console=console) as status:
                if current_model == 'gemini':
                    if gemini_chat_session is None:
                        from llm_inference.gemini_api import start_gemini_chat_session
                        gemini_chat_session = start_gemini_chat_session()
                    response = generate_content_with_quota_check(
                        user_input,
                        max_tokens=max_tokens,
                        chat_session=gemini_chat_session
                    )
                elif current_model == 'gemma':
                    response = run_gemma_inference(
                        user_input,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        chat_history=chat_history # Pass history for Gemma
                    )
            
            if response:
                display_name = "Severino" if current_model == 'gemma' else current_model.capitalize()
                console.print(f"[bold magenta]🐨 {display_name}:[/bold magenta] {response}")
                # Add both user input and model response to history for Gemma
                if current_model == 'gemma':
                    chat_history.append(f"<start_of_turn>user\n{user_input}<end_of_turn>\n<start_of_turn>model\n{response}<end_of_turn>")
                # For Gemini, the chat_session automatically manages history
            else:
                console.print(f"[bold red]No response from {current_model}.[/bold red]")

        except KeyboardInterrupt:
            console.print("[bold green]\nEnding chat session.[/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]\nAn error occurred during chat: {e}[/bold red]")


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
