# This file is for general utility functions that don't fit into other specific modules.
# Examples might include:
# - Data serialization/deserialization
# - File I/O helpers
# - String manipulation functions
# - Simple data structure operations

def greet(name: str) -> str:
    """Returns a greeting message."""
    return f"Hello, {name}!"

def calculate_average(numbers: list[float]) -> float:
    """Calculates the average of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

# Add more helper functions as your project grows.
