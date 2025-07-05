import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from config.settings import KOALA_THEME_LEVELS
from config.logging_config import logger

console = Console()

def display_llm_progress(current_tokens: int, max_tokens: int, message: str = ""):
    """
    Displays a Koala Climb progress indicator in the console.
    The koala's position on the tree is determined by the progress.
    Numerical progress is logged to the file.

    Args:
        current_tokens (int): The number of tokens generated so far.
        max_tokens (int): The maximum number of tokens expected.
        message (str): An optional message to display alongside the progress.
    """
    if max_tokens == 0: # Avoid division by zero
        progress_percent = 0
    else:
        progress_percent = (current_tokens / max_tokens) * 100

    # Determine koala's position based on progress
    # Levels are from bottom (0) to top (KOALA_THEME_LEVELS - 1)
    koala_level = int((current_tokens / max_tokens) * (KOALA_THEME_LEVELS - 1))
    if koala_level < 0: koala_level = 0
    if koala_level >= KOALA_THEME_LEVELS: koala_level = KOALA_THEME_LEVELS - 1

    # ASCII art for the tree and koala
    tree_art = r"""
      /\      
     /  \     
    /____\    
   /      \   
  /________\  
 /          \ 
/____________\
      ||      
      ||      
      ||      
"""
    tree_lines = tree_art.strip().split('\n')

    # Place the koala based on its level
    # The koala is 2 lines tall, so adjust placement accordingly
    koala_art = [
        "  (o o)   ",
        " (  V  )  "
    ]

    # Calculate where to insert the koala. Higher level means closer to the top.
    # The tree is 10 lines tall. Koala is 2 lines. 
    # koala_level 0 means bottom, so insert near line 8 (index 7)
    # koala_level 4 means top, so insert near line 2 (index 1)
    insert_index = len(tree_lines) - 2 - (koala_level * (len(tree_lines) - 2) // (KOALA_THEME_LEVELS - 1))
    if insert_index < 0: insert_index = 0

    # Create the visual representation
    display_lines = list(tree_lines) # Make a mutable copy
    display_lines[insert_index] = display_lines[insert_index][:2] + koala_art[0].strip() + display_lines[insert_index][2+len(koala_art[0].strip()):]
    display_lines[insert_index+1] = display_lines[insert_index+1][:2] + koala_art[1].strip() + display_lines[insert_index+1][2+len(koala_art[1].strip()):]

    tree_display = "\n".join(display_lines)

    # Prepare the panel content
    panel_content = Text(f"Progress: {progress_percent:.1f}%\n{message}", justify="center")
    panel_content.append(f"\n{tree_display}", style="green")

    console.print(Panel(panel_content, title="LLM Progress", border_style="blue"))

    # Log the numerical progress to the file
    logger.info(f"LLM Progress: {current_tokens}/{max_tokens} tokens ({progress_percent:.1f}%) - {message}")


# Example usage for testing this module directly
if __name__ == "__main__":
    # Basic logging setup for standalone test
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Simulate progress
    for i in range(KOALA_THEME_LEVELS + 1):
        tokens = int((i / KOALA_THEME_LEVELS) * 1000) # Simulate max_tokens = 1000
        display_llm_progress(tokens, 1000, f"Generating response... Step {i+1}")
        import time
        time.sleep(0.5)

    display_llm_progress(1000, 1000, "Generation Complete!")
