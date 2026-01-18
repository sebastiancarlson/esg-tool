import sys
import os

def read_stdin():
    """Reads input from stdin if piped."""
    if not sys.stdin.isatty():
        try:
            # If input is piped, read it
            return sys.stdin.read().strip()
        except Exception:
            # Handle cases where read fails
            return None
    return None