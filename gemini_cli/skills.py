import inspect
import functools
from typing import Callable, List, Dict, Any

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Callable] = {}

    def register(self, func: Callable):
        """Decorator to register a function as a skill."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._skills[func.__name__] = func
        return wrapper

    def get_tools(self) -> List[Callable]:
        """Returns a list of callable functions for the Gemini model."""
        return list(self._skills.values())

    def get_function_map(self) -> Dict[str, Callable]:
        """Returns a map of function names to callables (useful for manual execution)."""
        return self._skills

# Global registry instance
registry = SkillRegistry()
skill = registry.register

# --- Example Skills ---

@skill
def calculate_emissions(fuel_type: str, liters: float) -> str:
    """
    Calculates CO2 emissions for a given fuel type and volume.
    
    Args:
        fuel_type: Type of fuel (e.g., 'Diesel', 'Bensin', 'E85').
        liters: Volume in liters.
    
    Returns:
        A string describing the calculated emissions in kg.
    """
    factors = {
        'diesel': 2.54,
        'bensin': 2.36,
        'e85': 1.65,
        'biogas': 0.6
    }
    factor = factors.get(fuel_type.lower())
    if factor is None:
        return f"Unknown fuel type: {fuel_type}. Available: {', '.join(factors.keys())}"
    
    co2 = liters * factor
    return f"{co2:.2f} kg CO2e"

@skill
def list_directory(path: str = ".") -> str:
    """
    Lists the files and folders in a specific directory.
    
    Args:
        path: The directory path to list (defaults to current directory).
    """
    import os
    try:
        items = os.listdir(path)
        return f"Contents of {path}: {', '.join(items[:50])}" + ("..." if len(items) > 50 else "")
    except Exception as e:
        return f"Error listing directory: {e}"

@skill
def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a specified file.
    
    Args:
        file_path: The path to the file to read.
    """
    import os
    
    # List of paths to try
    paths_to_try = [
        file_path,
        os.path.abspath(file_path),
        os.path.join(os.getcwd(), file_path),
        file_path.replace("/", "\\"), # Try Windows style
        file_path.replace("\\", "/")  # Try Unix style
    ]
    
    for path in paths_to_try:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file at {path}: {e}"
                
    return f"Error: File not found. Tried: {', '.join(set(paths_to_try))}"

@skill
def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a specified file. Creates directories if they don't exist.
    
    Args:
        file_path: The path to the file to write to.
        content: The text content to write.
    """
    import os
    try:
        # Create directories if they don't exist and if the path has a directory component
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

@skill
def run_shell_command(command: str) -> str:
    """
    Executes a shell command and returns the output.
    
    Args:
        command: The shell command to execute.
    """
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
        if result.stderr:
            output += f"\nStderr: {result.stderr}"
        return output
    except Exception as e:
        return f"Error executing command: {e}"
