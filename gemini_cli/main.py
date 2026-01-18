import typer
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from typing import Optional
from typing_extensions import Annotated
import sys
import os

from . import config
from . import core
from . import utils

app = typer.Typer(help="Gemini CLI - AI in your terminal")
console = Console()

@app.command(name="config")
def configure(
    key: Annotated[Optional[str], typer.Option("--key", help="Your Google Gemini API Key")] = None
):
    """
    Configure the CLI settings (e.g., API Key).
    """
    if key:
        config.set_api_key(key)
        console.print(f"[green]API Key updated successfully![/green]")
    else:
        current_key = config.get_api_key()
        if current_key:
            masked_key = current_key[:4] + "*" * (len(current_key) - 8) + current_key[-4:]
            console.print(f"Current API Key: {masked_key}")
        else:
            console.print("[yellow]No API Key found. Set it with --key.[/yellow]")


@app.command()
def models():
    """
    List available Gemini models.
    """
    api_key = config.get_api_key()
    client = core.GeminiClient(api_key)
    
    available_models = client.list_models()
    
    table = Table(title="Available Gemini Models")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="magenta")
    
    for m in available_models:
        desc = m.description if hasattr(m, 'description') else "No description"
        # Truncate long descriptions
        if len(desc) > 80:
             desc = desc[:77] + "..."
        table.add_row(m.name, desc)
        
    console.print(table)


@app.command()
def ask(
    prompt: Annotated[Optional[str], typer.Argument(help="The prompt to send to Gemini")] = None,
    file: Annotated[Optional[str], typer.Option("--file", "-f", help="Path to a text file to include context")] = None,
    image: Annotated[Optional[str], typer.Option("--image", "-i", help="Path to an image file")] = None,
    model: Annotated[str, typer.Option("--model", "-m", help="Model to use")] = "gemini-2.0-flash-exp",
    system: Annotated[Optional[str], typer.Option("--system", "-s", help="System instructions")] = None,
    temp: Annotated[float, typer.Option("--temp", help="Temperature (0.0 - 1.0)")] = 0.7,
):
    """
    Ask a one-off question to Gemini. Supports piped input.
    """
    stdin_input = utils.read_stdin()
    
    # Combine prompt sources
    full_prompt = ""
    
    if stdin_input:
        full_prompt += f"Context:\n{stdin_input}\n\n"
        
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                full_prompt += f"File content ({file}):\n{file_content}\n\n"
        except Exception as e:
            console.print(f"[red]Error reading file {file}: {e}[/red]")
            raise typer.Exit(code=1)

    if prompt:
        full_prompt += f"Question: {prompt}"
    
    if not full_prompt.strip() and not image:
        console.print("[yellow]Please provide a prompt, a file, piped input, or an image.[/yellow]")
        raise typer.Exit(code=1)

    # Use default model if image is present but user selected a text-only model (basic heuristic)
    # Actually, Gemini 1.5/Pro Vision handles both. Let user override.
    
    api_key = config.get_api_key()
    try:
        client = core.GeminiClient(api_key)
        client.generate_content(
            model_name=model,
            prompt=full_prompt,
            image_path=image,
            system_instruction=system
        )
    except ValueError as e:
        console.print(f"[red]{e}[/red]")

@app.command()
def chat(
    model: Annotated[str, typer.Option("--model", "-m", help="Model to use")] = "gemini-2.0-flash-exp",
    system: Annotated[Optional[str], typer.Option("--system", "-s", help="System instructions")] = None,
):
    """
    Start an interactive chat session.
    """
    api_key = config.get_api_key()
    try:
        client = core.GeminiClient(api_key)
        chat_session = client.start_chat(model_name=model, system_instruction=system)
        
        console.print(f"[bold green]Starting chat with {model}. Type 'exit' to quit, '/reset' to clear history.[/bold green]")
        if system:
            console.print(f"[dim]System: {system}[/dim]")
            # Note: system instruction is usually set on model init, which start_chat uses.
            # Ideally we'd pass system instruction to start_chat's model init.
            # Since core.py handles this, we might need to adjust core.py if we want system prompts in chat.
            # But for now, let's assume the user knows what they are doing.
            pass

        while True:
            try:
                user_input = typer.prompt("You")
                
                if user_input.lower() in ["exit", "quit", "/exit"]:
                    break
                
                if user_input.lower() == "/reset":
                    chat_session = client.start_chat(model_name=model)
                    console.print("[yellow]Chat history reset.[/yellow]")
                    continue

                response = chat_session.send_message(user_input, stream=True)
                
                console.print("[bold blue]Gemini:[/bold blue]")
                for chunk in response:
                    print(chunk.text, end="", flush=True)
                print()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    except ValueError as e:
        console.print(f"[red]{e}[/red]")

if __name__ == "__main__":
    app()
