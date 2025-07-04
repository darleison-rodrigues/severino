# This file is for input validation functions specific to CLI commands.
# For example, you might validate file paths, numeric ranges, or specific string formats.

import click
import os

def validate_file_path(ctx, param, value):
    """
    Click callback to validate if a provided path is a valid file.
    Usage: @click.option('--file', callback=validate_file_path)
    """
    if value and not os.path.isfile(value):
        raise click.BadParameter(f"File not found: '{value}'")
    return value

def validate_positive_number(ctx, param, value):
    """
    Click callback to validate if a number is positive.
    Usage: @click.option('--count', type=int, callback=validate_positive_number)
    """
    if value is not None and value <= 0:
        raise click.BadParameter(f"'{param.name}' must be a positive number.")
    return value

# Add more validation functions as needed for your CLI arguments and options.
