import click
from llm_inference.gemma_local import run_gemma_inference, load_gemma_model
from config.settings import MAX_GEMMA_OUTPUT_TOKENS, AGENT_EMOJI, DEFAULT_GEMMA_MODEL_PATH, PROJECT_ROOT
from config.logging_config import logger
import os
from rich.console import Console
from rich.status import Status

from packages.core.state_manager import StateManager

console = Console()
state_manager = StateManager(session_id="cli_session") # Using a fixed session ID for CLI

# The main CLI group for the Severino application.
# All commands will be registered under this group.
@click.group()
def cli():
    """
    Severino: A CLI for ML monitoring assistance using Gemma.
    Use 'severino <command> --help' for more information on each command.
    """
    pass # No specific initialization needed for the main group itself

@cli.command()
@click.argument('prompt')
@click.option('--model-path', type=click.Path(exists=True), required=False,
              help='Absolute path to the Gemma GGUF model file (e.g., data/models/gemma-2b-it.Q4_K_M.gguf).')
@click.option('--max-tokens', default=256, type=int,
              help='Maximum number of tokens to generate locally by Gemma.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the Gemma model (0.0-1.0). Higher values are more creative.')
@click.option('--development', is_flag=True, default=False,
              help='Use default Gemma model path for development (data/models/gemma-2b-it.Q4_K_M.gguf).')
def gemma(prompt: str, model_path: str, max_tokens: int, temperature: float, development: bool):
    """
    Runs local inference using the Gemma model.
    Ideal for quick insights, coding help, or general tasks where speed and privacy are key.
    """
    if development and not model_path:
        model_path = DEFAULT_GEMMA_MODEL_PATH
        console.print(f"[bold yellow]Development mode: Using default model path: {model_path}[/bold yellow]")
    elif not model_path:
        raise click.BadParameter("'--model-path' is required unless '--development' flag is used.")

    console.print(f"[bold blue]Running Gemma locally for:[/bold blue] '{prompt}'")

    try:
        # Attempt to load the Gemma model. This will raise an error if the model's not found.
        # The model is loaded once and reused across subsequent 'gemma' calls.
        load_gemma_model(model_path)
        response = run_gemma_inference(prompt, max_tokens, temperature)
        console.print("\n[bold green]--- Gemma Response ---[/bold green]")
        console.print(response)
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print(f"[bold red]Gemma model not found at '{model_path}'. Please ensure the path is correct.[/bold red]")
        
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during Gemma inference: {e}[/bold red]")
        


@cli.command()
@click.option('--model-path', type=click.Path(exists=True), required=False,
              help='Absolute path to the Gemma GGUF model file (e.g., data/models/gemma-2b-it.Q4_K_M.gguf).')
@click.option('--max-tokens', default=512, type=int,
              help='Maximum number of tokens for model generation in chat.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the Gemma model (0.0-1.0). Higher values are more creative.')
@click.option('--development', is_flag=True, default=False,
              help='Use default Gemma model path for development (data/models/gemma-2b-it.Q4_K_M.gguf).')
def chat(model_path: str, max_tokens: int, temperature: float, development: bool):
    """
    Starts an interactive chat session with the Gemma LLM.
    Type 'exit' or 'quit' to end the session.
    """
    if development and not model_path:
        model_path = DEFAULT_GEMMA_MODEL_PATH
        console.print(f"[bold yellow]Development mode: Using default model path: {model_path}[/bold yellow]")
    elif not model_path:
        raise click.BadParameter("'--model-path' is required unless '--development' flag is used.")

    console.print(f"[bold green]Starting interactive chat with Gemma.[/bold green] Type '[bold red]exit[/bold red]' or '[bold red]quit[/bold red]' to end.")

    chat_history = []
    
    # Load system prompt and add to chat history
    system_prompt_path = os.path.join(PROJECT_ROOT, "system_prompt.txt")
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt_content = f.read()
        chat_history.append(f"<start_of_turn>system\n{system_prompt_content}<end_of_turn>\n")
        console.print("[green]System prompt loaded and added to chat history.[/green]")
    except FileNotFoundError:
        console.print(f"[bold red]Warning: system_prompt.txt not found at {system_prompt_path}. Chat will proceed without it.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error loading system_prompt.txt: {e}. Chat will proceed without it.[/bold red]")

    try:
        load_gemma_model(model_path) # Ensure Gemma model is loaded once
        console.print("[green]Gemma model loaded for chat.[/green]")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print(f"[bold red]Gemma model not found at '{model_path}'. Please ensure the path is correct.[/bold red]")
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during Gemma model loading: {e}[/bold red]")
        return
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input:
                continue

            with Status("[bold yellow]Thinking...[/bold yellow]", spinner="dots", console=console) as status:
                response = run_gemma_inference(user_input, max_tokens, temperature, chat_history=chat_history)
                console.print(f"{AGENT_EMOJI} {response}")
                # Append user input and model response to history for next turn
                chat_history.append(f"<start_of_turn>user\n{user_input}<end_of_turn>\n")
                chat_history.append(f"<start_of_turn>model\n{response}<end_of_turn>\n")

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
#     (Conceptual: would involve reading logs and passing to Gemma)
#     """
#     logger.info(f"Analyzing log file: {log_file}")
#     click.echo(f"Analyzing {log_file} for insights...")
#     # Example: Read log content, then use an LLM to summarize/identify issues
#     # with open(log_file, 'r') as f:
#     #     log_content = f.read()
#     #
#     # # Use Gemma for quick summary, or for deeper analysis
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
#     (Conceptual: would involve data retrieval and Gemma for structured report generation)
#     """
#     logger.info(f"Generating {report_type} report.")
#     click.echo(f"Generating a {report_type} performance report...")
#     # Example: Retrieve data from cache/database, then use Gemma to format a report
#     # data_for_report = retrieve_data(report_type)
#     # report_prompt = f"Generate a {report_type} performance report based on this data: {data_for_report}"
#     # report = generate_content_with_quota_check(report_prompt, max_tokens=2000)
#     # if report:
#     #     click.echo(f"\n--- Generated Report ---\n{report}")
#     logger.info("Report generation command executed (conceptual).")