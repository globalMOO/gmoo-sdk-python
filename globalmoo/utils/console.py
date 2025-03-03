# -*- coding: utf-8 -*-
"""Rich console utilities for formatted output."""
from rich.console import Console
from rich.theme import Theme
from rich.text import Text

# Define symbols - using ASCII for better compatibility
CHECK_MARK = "+"       # Simple plus
X_MARK = "x"         # Simple x
IN_SET = "in"        # Plain text

# Create a custom theme for consistent styling
custom_theme = Theme({
    'info': 'cyan',
    'success': 'green',
    'error': 'red',
    'warning': 'yellow',
    'satisfied': 'bold green',
    'unsatisfied': 'bold red',
})

console = Console(
    theme=custom_theme,
    force_terminal=True,
    color_system="auto"
)

def print_satisfaction_status(objective_num: int, satisfied: bool, detail: str):
    """Print the satisfaction status of an objective with checkmark/x and detail."""
    symbol = f"({CHECK_MARK})" if satisfied else f"({X_MARK})"
    style = "satisfied" if satisfied else "unsatisfied"
    
    text = Text()
    text.append(f"  Objective {objective_num}: ", style="default")
    text.append(symbol, style=style)
    
    # Simple string replacement for the detail text
    detail_text = detail.replace(' within ', ' in ').replace(' in ', f' {IN_SET} ')
    text.append(f" - {detail_text}", style="default")
    
    console.print(text)

def print_section_header(title: str):
    """Print a section header with consistent styling."""
    console.print(f"\n[bold]{title}[/bold]")

def print_values(label: str, values: list, precision: int = 4):
    """Print a list of values with consistent formatting."""
    formatted_values = [f"{x:.{precision}f}" for x in values]
    console.print(f"  {label}: {formatted_values}")

def print_info(message: str):
    """Print an info message."""
    console.print(f"[info]{message}[/info]")

def print_success(message: str):
    """Print a success message."""
    console.print(f"[success]{message}[/success]")

def print_error(message: str):
    """Print an error message."""
    console.print(f"[error]{message}[/error]")

def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[warning]{message}[/warning]")