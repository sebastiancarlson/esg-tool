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
def list_directory_contents(path: str = ".") -> str:
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
