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
from .skills import registry

app = typer.Typer(help="Gemini CLI - AI in your terminal")
console = Console()

extensions_app = typer.Typer(help="Manage Gemini CLI extensions")
app.add_typer(extensions_app, name="extensions")

conductor_app = typer.Typer(help="Conductor agentic workflows")
app.add_typer(conductor_app, name="conductor")

@conductor_app.command(name="list")
def conductor_list():
    """
    List available Conductor workflows.
    """
    import tomllib
    conductor_dir = os.path.join(os.path.dirname(__file__), "extensions", "conductor", "commands", "conductor")
    if not os.path.exists(conductor_dir):
        console.print("[red]Conductor extension not found. Install it first.[/red]")
        return
        
    table = Table(title="Available Conductor Workflows")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    
    for file in os.listdir(conductor_dir):
        if file.endswith(".toml"):
            with open(os.path.join(conductor_dir, file), "rb") as f:
                data = tomllib.load(f)
                table.add_row(file.replace(".toml", ""), data.get("description", "No description"))
                
    console.print(table)

@conductor_app.command(name="run")
def conductor_run(
    workflow: str,
    model: Annotated[str, typer.Option("--model", "-m", help="Model to use")] = "gemini-2.0-flash-exp"
):
    """
    Run a specific Conductor workflow.
    """
    import tomllib
    workflow_path = os.path.join(os.path.dirname(__file__), "extensions", "conductor", "commands", "conductor", f"{workflow}.toml")
    
    if not os.path.exists(workflow_path):
        console.print(f"[red]Workflow '{workflow}' not found.[/red]")
        return
        
    with open(workflow_path, "rb") as f:
        data = tomllib.load(f)
        system_prompt = data.get("prompt", "")
        
    if not system_prompt:
        console.print(f"[red]Workflow '{workflow}' has no prompt defined.[/red]")
        return
        
    console.print(f"[bold blue]Running Conductor workflow: {workflow}[/bold blue]")
    
    # Pre-scan conductor directory to provide immediate context and avoid "not set up" errors
    initial_context = ""
    if os.path.exists("conductor"):
        files = os.listdir("conductor")
        initial_context = f"\n\nNOTE: The 'conductor/' directory already exists and contains: {', '.join(files)}. The environment is likely already set up."
    
    # Start a chat session with the workflow's prompt as the system instruction
    chat(model=model, system=system_prompt + initial_context)

@extensions_app.command()
def install(url: str):
    """
    Install an extension from a Git repository.
    """
    import subprocess
    import shutil
    
    repo_name = url.split("/")[-1].replace(".git", "")
    target_dir = os.path.join(os.path.dirname(__file__), "extensions", repo_name)
    
    if os.path.exists(target_dir):
        console.print(f"[yellow]Extension '{repo_name}' is already installed. Reinstalling...[/yellow]")
        shutil.rmtree(target_dir)
        
    console.print(f"Installing extension from [cyan]{url}[/cyan]...")
    try:
        subprocess.run(["git", "clone", url, target_dir], check=True, capture_output=True)
        console.print(f"[green]Successfully installed '{repo_name}'![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install extension: {e.stderr.decode()}[/red]")

@app.command()
def skills():
    """
    List available agent skills/tools.
    """
    tools = registry.get_tools()
    table = Table(title="Available Agent Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    
    for tool in tools:
        table.add_row(tool.__name__, tool.__doc__.strip().split('\n')[0] if tool.__doc__ else "No description")
    
    console.print(table)

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
            system_instruction=system,
            tools=registry.get_tools()
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
        # Pass tools to start_chat. With enable_automatic_function_calling=True in core.py, 
        # the SDK will handle execution loop.
        chat_session = client.start_chat(
            model_name=model, 
            system_instruction=system,
            tools=registry.get_tools()
        )
        
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

                # Disable streaming if tools are active (SDK limitation)
                tools_active = len(registry.get_tools()) > 0
                stream = not tools_active
                
                response = chat_session.send_message(user_input, stream=stream)
                
                # Manual Function Calling Loop
                from google.ai.generativelanguage_v1beta.types import content
                
                while True:
                    # Check for function calls in the response
                    function_calls = []
                    try:
                        if response.candidates:
                             for part in response.candidates[0].content.parts:
                                if part.function_call:
                                    function_calls.append(part.function_call)
                    except AttributeError:
                        pass 

                    if function_calls:
                        response_parts = []
                        
                        for function_call in function_calls:
                            # console.print(f"[dim]Tool Call: {function_call.name}[/dim]")
                            
                            tool_name = function_call.name
                            tool_args = dict(function_call.args)
                            
                            # Find the function in our registry
                            tool_func = registry.get_function_map().get(tool_name)
                            
                            if tool_func:
                                try:
                                    # Execute the tool
                                    result = tool_func(**tool_args)
                                    
                                    response_parts.append(content.Part(
                                        function_response=content.FunctionResponse(
                                            name=tool_name,
                                            response={"result": result}
                                        )
                                    ))
                                except Exception as e:
                                    error_msg = f"Error executing {tool_name}: {str(e)}"
                                    console.print(f"[red]{error_msg}[/red]")
                                    response_parts.append(content.Part(
                                        function_response=content.FunctionResponse(
                                            name=tool_name,
                                            response={"error": error_msg}
                                        )
                                    ))
                            else:
                                 console.print(f"[red]Tool '{tool_name}' not found.[/red]")
                                 response_parts.append(content.Part(
                                        function_response=content.FunctionResponse(
                                            name=tool_name,
                                            response={"error": f"Tool {tool_name} not found"}
                                        )
                                    ))

                        # Send ALL function responses back to the model in one go
                        response = chat_session.send_message(
                            response_parts,
                            stream=stream
                        )
                    else:
                        # No function call, just print the text response and break the loop
                        console.print("[bold blue]Gemini:[/bold blue]")
                        if stream:
                            try:
                                for chunk in response:
                                    print(chunk.text, end="", flush=True)
                                print()
                            except ValueError:
                                # Sometimes a chunk might not have text if it was a weird stop sequence
                                pass
                        else:
                             # Non-streaming response contains the full text
                             # Check if it has text parts
                             if response.text:
                                print(response.text)
                        break

            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    except ValueError as e:
        console.print(f"[red]{e}[/red]")

if __name__ == "__main__":
    app()
