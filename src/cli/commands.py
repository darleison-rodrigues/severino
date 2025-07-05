import click
from llm_inference.local_llm import run_local_llm_inference, load_local_llm
from config.settings import MAX_LOCAL_LLM_OUTPUT_TOKENS, AGENT_EMOJI, DEFAULT_LOCAL_LLM_MODEL_PATH, PROJECT_ROOT, KOALA_THEME_ENABLED
from config.logging_config import logger
from config.system_prompts import SYSTEM_PROMPT_CODE_EXPERT
import os
import subprocess
from rich.console import Console
from rich.status import Status
from utils.ui_elements import display_llm_progress

from src.packages.core.state_manager import StateManager
from src.utils.code_integrity import get_git_status, generate_file_checksum
from src.utils.code_parser import parse_python_file

console = Console()
state_manager = StateManager(session_id="cli_session", project_root=PROJECT_ROOT) # Using a fixed session ID for CLI

# The main CLI group for the Severino application.
# All commands will be registered under this group.
@click.group()
def cli():
    """
    Severino: A CLI for ML monitoring assistance using a local LLM.
    Use 'severino <command> --help' for more information on each command.
    """
    pass # No specific initialization needed for the main group itself

@cli.command()
def status():
    """Displays the current status of the application."""
    console.print("[bold green]Application Status:[/bold green] OK")

@cli.command()
@click.argument('path', default='.', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def code(path):
    """Starts the UI and begins building a knowledge graph of the codebase.

    PATH: The path to the codebase directory (defaults to current directory).
    """
    console.print(f"[bold blue]Starting Severino UI for codebase: {path}[/bold blue]")

    # Start the Python API in the background
    api_process = subprocess.Popen(["python", "-m", "src.api"], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    console.print("[green]Severino API started in the background.[/green]")

    # Start the Electron UI in the background
    electron_ui_path = os.path.join(PROJECT_ROOT, "electron-llm-ui")
    ui_process = subprocess.Popen(["npm", "start"], cwd=electron_ui_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    console.print("[green]Severino UI started in the background.[/green]")

    # Check for errors from the UI process
    stdout, stderr = ui_process.communicate()
    if ui_process.returncode != 0:
        console.print(f"[bold red]Error starting UI (Exit Code: {ui_process.returncode}):[/bold red]")
        if stdout:
            console.print(f"[red]Stdout:[/red] {stdout.decode()}")
        if stderr:
            console.print(f"[red]Stderr:[/red] {stderr.decode()}")
        console.print("[bold red]Please check the UI logs for more details.[/bold red]")
        return # Exit if UI failed to start

    console.print(f"[bold yellow]Building initial knowledge graph... (This may take a moment)[/bold yellow]")
    
    # Perform Git status check
    git_status = get_git_status(path)
    console.print("\n[bold yellow]--- Git Status ---\[/bold yellow]")
    for status_type, files in git_status.items():
        if files:
            console.print(f"[yellow]{status_type.capitalize()}:[/yellow]")
            for f in files:
                console.print(f"  - {f}")
        else:
            console.print(f"[yellow]No {status_type} files.[/yellow]")

    # Process Python files for knowledge graph
    console.print("\n[bold yellow]--- Parsing Python Files for Knowledge Graph ---[/bold yellow]")
    parsed_files_count = 0
    for root, _, files in os.walk(path):
        # Exclude common large/irrelevant directories
        if '.git' in root or 'node_modules' in root or '.venv' in root or '__pycache__' in root or '.severino' in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, path)
                
                try:
                    parsed_data = parse_python_file(full_path)
                    file_checksum = parsed_data["file_checksum"]
                    last_modified = parsed_data["last_modified"]

                    # Check if file entity already exists
                    existing_file_entity = state_manager.get_code_entity(full_path)
                    file_entity_id = None

                    if existing_file_entity:
                        if existing_file_entity["checksum"] != file_checksum:
                            # Update existing entity if checksum changed
                            state_manager.update_code_entity_checksum(full_path, file_checksum, last_modified)
                            file_entity_id = existing_file_entity["entity_id"]
                            console.print(f"[yellow]Updated:[/yellow] {relative_path}")
                        else:
                            file_entity_id = existing_file_entity["entity_id"]
                            console.print(f"[green]Skipped (no change):[/green] {relative_path}")
                            continue # Skip parsing if no change
                    else:
                        # Add new file entity
                        file_entity_id = state_manager.add_code_entity(
                            path=full_path,
                            type="file",
                            name=file,
                            checksum=file_checksum,
                            last_modified=last_modified,
                            embedding=parsed_data["file_embedding"] # Assuming file_embedding is returned by parse_python_file
                        )
                        console.print(f"[green]Parsed:[/green] {relative_path}")
                    
                    # Store entities and relationships
                    for entity_data in parsed_data["entities"]:
                        # For sub-entities, create a unique path by combining file path and entity name
                        sub_entity_path = f"{full_path}::{entity_data['name']}"
                        state_manager.add_code_entity(
                            path=sub_entity_path,
                            type=entity_data["type"],
                            name=entity_data["name"],
                            checksum="", # Checksum for sub-entities is complex, leave blank for now
                            last_modified="", # Leave blank for now
                            embedding=entity_data["embedding"] # Pass the embedding
                        )

                    for rel_data in parsed_data["relationships"]:
                        # This part needs to resolve source/target paths to entity_ids
                        # For now, we'll just log them.
                        # A full implementation would involve looking up entity_ids for source_path and target_path
                        # and then adding the relationship using those IDs.
                        pass # Placeholder for relationship storage

                    parsed_files_count += 1

                except Exception as e:
                    console.print(f"[bold red]Error parsing {relative_path}: {e}[/bold red]")
                    logger.error(f"Error parsing {full_path}: {e}", exc_info=True)

    console.print(f"\n[bold green]Parsed {parsed_files_count} Python files.[/bold green]")
    console.print(f"\n[bold green]Knowledge graph for {path} initialized.[/bold green]")
    console.print("[bold green]Severino is ready![/bold green]")

@cli.command()
@click.argument('prompt')
@click.option('--model-path', type=click.Path(exists=True), required=False,
              help='Absolute path to the local LLM GGUF model file (e.g., data/models/model.gguf).')
@click.option('--max-tokens', default=256, type=int,
              help='Maximum number of tokens to generate locally by the LLM.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the local LLM (0.0-1.0). Higher values are more creative.')
@click.option('--development', is_flag=True, default=False,
              help='Use default local LLM model path for development (data/models/gemma-2b-it.Q4_K_M.gguf).')
def gemma(prompt: str, model_path: str, max_tokens: int, temperature: float, development: bool):
    """
    Runs local inference using the local LLM.
    Ideal for quick insights, coding help, or general tasks where speed and privacy are key.
    """
    if development and not model_path:
        model_path = DEFAULT_LOCAL_LLM_MODEL_PATH
        console.print(f"[bold yellow]Development mode: Using default model path: {model_path}[/bold yellow]")
    elif not model_path:
        raise click.BadParameter("'--model-path' is required unless '--development' flag is used.'")

    console.print(f"[bold blue]Running local LLM for:[/bold blue] '{prompt}'")

    try:
        # Attempt to load the LLM model. This will raise an error if the model's not found.
        # The model is loaded once and reused across subsequent calls.
        load_local_llm(model_path)
        response_data = run_local_llm_inference(prompt, max_tokens, temperature)
        console.print("\n[bold green]--- Local LLM Response ---\[/bold green]")
        console.print(response_data['generated_text'])
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print(f"[bold red]Local LLM model not found at '{model_path}'. Please ensure the path is correct.[/bold red]")
        
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during local LLM inference: {e}[/bold red]")
        


@cli.command()
@click.option('--model-path', type=click.Path(exists=True), required=False,
              help='Absolute path to the local LLM GGUF model file (e.g., data/models/model.gguf).')
@click.option('--max-tokens', default=512, type=int,
              help='Maximum number of tokens for model generation in chat.')
@click.option('--temperature', default=0.7, type=float,
              help='Creativity of the local LLM (0.0-1.0). Higher values are more creative.')
@click.option('--development', is_flag=True, default=False,
              help='Use default local LLM model path for development (data/models/gemma-2b-it.Q4_K_M.gguf).')
def chat(model_path: str, max_tokens: int, temperature: float, development: bool):
    """
    Starts an interactive chat session with the local LLM.
    Type 'exit' or 'quit' to end the session.
    """
    if development and not model_path:
        model_path = DEFAULT_LOCAL_LLM_MODEL_PATH
        console.print(f"[bold yellow]Development mode: Using default model path: {model_path}[/bold yellow]")
    elif not model_path:
        raise click.BadParameter("'--model-path' is required unless '--development' flag is used.'")

    console.print(f"[bold green]Starting interactive chat with local LLM.[/bold green] Type '[bold red]exit[/bold red]' or '[bold red]quit[/bold red]' to end.'")

    chat_history = []
    
    # Load system prompt and add to chat history
    system_prompt_content = SYSTEM_PROMPT_CODE_EXPERT # Use the imported system prompt
    chat_history.append(f"<start_of_turn>system\n{system_prompt_content}<end_of_turn>\n")
    console.print("[green]System prompt loaded and added to chat history.[/green]")

    try:
        load_local_llm(model_path) # Ensure LLM model is loaded once
        console.print("[green]Local LLM model loaded for chat.[/green]")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print(f"[bold red]Local LLM model not found at '{model_path}'. Please ensure the path is correct.[/bold red]")
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during local LLM model loading: {e}[/bold red]")
        return
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input:
                continue

            with Status("[bold yellow]Thinking...[/bold yellow]", spinner="dots", console=console) as status:
                response_data = run_local_llm_inference(user_input, max_tokens, temperature, chat_history=chat_history)
                generated_text = response_data['generated_text']
                tokens_generated = response_data['tokens_generated']

                if KOALA_THEME_ENABLED:
                    display_llm_progress(tokens_generated, max_tokens, "Generating response...")
                
                console.print(f"{AGENT_EMOJI} {generated_text}")
                # Append user input and model response to history for next turn
                chat_history.append(f"<start_of_turn>user\n{user_input}<end_of_turn>\n")
                chat_history.append(f"<start_of_turn>model\n{generated_text}<end_of_turn>\n")

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
    Analyzes an ML model log file using LLMs to identify issues.
#     (Conceptual: would involve reading logs and passing to local LLM)
#     """
    logger.info(f"Analyzing log file: {log_file}")
#     click.echo(f"Analyzing {log_file} for insights...")
#     # Example: Read log content, then use an LLM to summarize/identify issues
#     # with open(log_file, 'r') as f:
#     #     log_content = f.read()
#     #
#     # # Use local LLM for quick summary, or for deeper analysis
#     # summary_prompt = f"Summarize key errors or anomalies from this log: {log_content[:2000]}..."
#     # summary = run_local_llm_inference(summary_prompt, max_tokens=500)
#     # click.echo(f"\n--- Log Summary ---\n{summary}")
#     logger.info("Log analysis command executed (conceptual).")

# @cli.command()
# @click.option('--report-type', type=click.Choice(['daily', 'weekly', 'monthly']), default='daily',
#               help='Type of report to generate.')
# def generate_report(report_type: str):
#     """
    Generates a performance report based on collected data.
#     (Conceptual: would involve data retrieval and local LLM for structured report generation)
#     """
    logger.info(f"Generating {report_type} report.")
#     click.echo(f"Generating a {report_type} performance report...")
#     # Example: Retrieve data from cache/database, then use local LLM to format a report
#     # data_for_report = retrieve_data(report_type)
#     # report_prompt = f"Generate a {report_type} performance report based on this data: {data_for_report}"
#     # report = generate_content_with_quota_check(report_prompt, max_tokens=2000)
#     # if report:
#     #     click.echo(f"\n--- Generated Report ---\n{report}")
#     logger.info("Report generation command executed (conceptual).")
