import google.generativeai as genai
from rich.console import Console
from rich.markdown import Markdown
import sys

# Configure global settings
console = Console()

class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is missing. Please set GEMINI_API_KEY environment variable or run 'gemini config --key <YOUR_KEY>'")
        genai.configure(api_key=api_key)

    def list_models(self):
        """Lists available Gemini models."""
        try:
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m)
            return models
        except Exception as e:
            console.print(f"[bold red]Error listing models:[/bold red] {e}")
            return []

    def generate_content(self, model_name: str, prompt: str, image_path: str = None, system_instruction: str = None, tools: list = None, stream: bool = True):
        """Generates content (one-shot)."""
        try:
            model = genai.GenerativeModel(model_name, system_instruction=system_instruction, tools=tools)
            
            contents = [prompt]
            if image_path:
                import PIL.Image
                try:
                    img = PIL.Image.open(image_path)
                    contents.append(img)
                except Exception as e:
                    console.print(f"[bold red]Error loading image:[/bold red] {e}")
                    return

            # If tools are provided, automatic function calling might be needed. 
            # For simple one-shot, we rely on the SDK's handling or just return the result.
            # Note: stream=True with tools can be complex.
            response = model.generate_content(contents, stream=stream)
            
            if stream:
                for chunk in response:
                    # Check if the chunk has text; tool calls might not have text immediately
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print() # Newline at the end
            else:
                return response.text
        except Exception as e:
            # Handle cases where response is blocked or contains only tool calls (no text)
            if "text" in str(e) and tools:
                 console.print(f"[yellow]Model attempted to use a tool (One-shot tool use requires chat mode or handling 'parts').[/yellow]")
                 # In a real implementation, we would handle the FunctionCall part here.
            else:
                console.print(f"[bold red]Error generating content:[/bold red] {e}")

    def start_chat(self, model_name: str, history: list = None, system_instruction: str = None, tools: list = None):
        """Starts a chat session."""
        try:
            model = genai.GenerativeModel(model_name, system_instruction=system_instruction, tools=tools)
            # enable_automatic_function_calling=True allows the SDK to execute the code and return the result to the model automatically.
            chat = model.start_chat(history=history or [], enable_automatic_function_calling=True if tools else False)
            return chat
        except Exception as e:
            console.print(f"[bold red]Error starting chat:[/bold red] {e}")
            return None
