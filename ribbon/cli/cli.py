# ribbon/cli.py
import json
import os
import urllib
import re
import inspect
import copy
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from ribbon.config import RIBBON_HOME, CONFIG_FILE, CACHE_DIR, TASKS_DIR, CONTAINER_DIR, GITHUB_API_URL, TASKS_VERSION
from ribbon.config.parse_config import write_config_file

app = typer.Typer(help="Manage Ribbon task definitions.", add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

run_app = typer.Typer(help="Run a task from the active Ribbon-Tasks module.", add_completion=False, no_args_is_help=True, rich_markup_mode="rich")
console = Console()

### HELPER FUNCTIONS ###
def _version_sort_key(tag):
    """Sort semver-like tags ahead of custom names."""
    semver_match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", tag)
    if semver_match:
        major, minor, patch = map(int, semver_match.groups())
        return (2, major, minor, patch, tag)

    loose_match = re.search(r"(\d+)\.(\d+)\.(\d+)", tag)
    if loose_match:
        major, minor, patch = map(int, loose_match.groups())
        return (1, major, minor, patch, tag)

    return (0, 0, 0, 0, tag)

def _load_tasks_file(version):
    tasks_file = TASKS_DIR / version / "Ribbon-Tasks" / "ribbon_tasks" / "tasks.json"
    if not tasks_file.exists():
        return None, tasks_file

    try:
        with open(tasks_file) as f:
            return json.load(f), tasks_file
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in task definition file '{tasks_file}': {e}[/red]")
        return None, tasks_file
    except Exception as e:
        console.print(f"[red]Error reading task definition file '{tasks_file}': {e}[/red]")
        return None, tasks_file

def _extract_inputs_from_command(command):
    seen = set()
    ordered_inputs = []
    for match in re.findall(r"\{([^{}]+)\}", command or ""):
        if match not in seen:
            seen.add(match)
            ordered_inputs.append(match)
    return ordered_inputs

### FETCHING RELEASES ###
def fetch_remote_releases(quiet=False):
    """Fetch available releases from GitHub API using urllib."""
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen(GITHUB_API_URL) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                return data
            else:
                if not quiet:
                    console.print(f"[yellow]Warning: Could not fetch online releases (HTTP {response.getcode()}).[/yellow]")
                return []
    except urllib.error.URLError as e:
        if not quiet:
            console.print(f"[yellow]Warning: Could not fetch online releases: {e}[/yellow]")
        return []
    except json.JSONDecodeError as e:
        if not quiet:
            console.print(f"[yellow]Warning: Could not parse online releases response: {e}[/yellow]")
        return []

def fetch_local_releases():
    """Fetch local releases from the cache directory."""
    local_releases = [item.name for item in TASKS_DIR.iterdir() if item.is_dir()]
    return sorted(local_releases, key=_version_sort_key, reverse=True)

### MAIN COMMANDS ###

def list_versions_cmd(
    offline: bool = False,
    output_json: bool = False
):
    """List available Ribbon-Tasks versions."""
    releases = fetch_remote_releases(quiet=output_json) if not offline else []
    remote_release_tags = {release.get("tag_name") for release in releases}

    local_releases = [
        tag for tag in fetch_local_releases()
        if tag not in remote_release_tags
    ]

    if output_json:
        output = {
            "active_version": TASKS_VERSION,
            "official_releases": [
                {
                    "tag": release.get("tag_name", "Unknown"),
                    "published_at": release.get("published_at"),
                    "is_active": release.get("tag_name") == TASKS_VERSION,
                }
                for release in releases
            ],
            "custom_releases": [],
        }
        for tag in local_releases:
            modified_date = datetime.fromtimestamp((TASKS_DIR / tag).stat().st_mtime).strftime("%Y-%m-%d")
            output["custom_releases"].append(
                {"tag": tag, "modified_at": modified_date, "is_active": tag == TASKS_VERSION}
            )
        console.print(json.dumps(output, indent=2))
        return

    if not offline:
        table = Table(title="Official Releases", box=None, padding=(0, 2))
        table.add_column("Status", justify="center", width=6)
        table.add_column("Version", style="cyan")
        table.add_column("Released At", style="dim")

        if releases:
            for release in releases:
                tag = release.get("tag_name", "Unknown")
                published = release.get("published_at", "Unknown date")[:10]
                is_active = tag == TASKS_VERSION
                status = "[green]*[/green]" if is_active else ""
                row_style = "bold green" if is_active else ""
                table.add_row(status, tag, published, style=row_style)
            console.print(table)
            console.print("")
        else:
            console.print("\n[dim italic]No official releases found or unreachable.[/dim italic]")

    custom_table = Table(title="Custom Releases", box=None, padding=(0, 2))
    custom_table.add_column("Status", justify="center", width=6)
    custom_table.add_column("Version", style="cyan")
    custom_table.add_column("Modified At", style="dim")

    if not local_releases:
        console.print("\n[dim italic]No local versions found.[/dim italic]")
    else:
        for tag in local_releases:
            is_active = tag == TASKS_VERSION
            status = "[green]*[/green]" if is_active else ""
            modified_date = datetime.fromtimestamp((TASKS_DIR / tag).stat().st_mtime).strftime("%Y-%m-%d")
            row_style = "bold green" if is_active else ""
            custom_table.add_row(status, tag, modified_date, style=row_style)
        console.print(custom_table)

    console.print("")

def list_tasks_function(
    version: Optional[str] = None,
    verbose: bool = False,
    output_json: bool = False
):
    """List tasks for a Ribbon-Tasks version."""
    target_version = version or TASKS_VERSION
    tasks, tasks_file = _load_tasks_file(target_version)

    if tasks is None:
        console.print(f"[red]Error: Could not load tasks for version '{target_version}'.[/red]")
        console.print(f"Expected task definition file: {tasks_file}")
        raise typer.Exit(code=1)

    task_names = sorted(tasks.keys())

    if output_json:
        if verbose:
            payload = {
                "version": target_version,
                "is_active_version": target_version == TASKS_VERSION,
                "tasks": [
                    {
                        "name": task_name,
                        "description": tasks[task_name].get("description"),
                        "container": tasks[task_name].get("container"),
                        "inputs": _extract_inputs_from_command(tasks[task_name].get("command", "")),
                    }
                    for task_name in task_names
                ],
            }
        else:
            payload = {
                "version": target_version,
                "is_active_version": target_version == TASKS_VERSION,
                "tasks": task_names,
            }
        console.print(json.dumps(payload, indent=2))
        return

    version_label = " (active)" if target_version == TASKS_VERSION else ""
    title = f"Tasks in Ribbon-Tasks {target_version}{version_label}"
    
    if not verbose:
        table = Table(title=title, box=None, show_header=False, padding=(0, 2))
        table.add_column("Task", style="cyan")
        for task_name in task_names:
            table.add_row(f"- {task_name}")
        console.print(table)
    else:
        table = Table(title=title, box=None, padding=(0, 2))
        table.add_column("Task", style="bold cyan")
        table.add_column("Description", style="dim")
        table.add_column("Container", style="magenta")
        table.add_column("Inputs", style="dim")
        
        for task_name in task_names:
            task = tasks.get(task_name, {})
            inputs = _extract_inputs_from_command(task.get("command", ""))
            table.add_row(
                task_name,
                task.get('description', 'N/A'),
                task.get('container', 'N/A'),
                ', '.join(inputs) if inputs else "(none)"
            )
        console.print(table)
    
    console.print("")

@app.command(name="list")
def list_cmd(
    target: str = typer.Argument("versions", help="What to list: versions or tasks."),
    version: Optional[str] = typer.Option(None, "--version", help="Version to list tasks for."),
    verbose: bool = typer.Option(False, "--verbose", help="Show task details."),
    offline: bool = typer.Option(False, "--offline", help="Skip online release lookup."),
    output_json: bool = typer.Option(False, "--json", help="Output results as JSON.")
):
    """List available Ribbon-Tasks versions or tasks."""
    if target == "tasks":
        list_tasks_function(version, verbose, output_json)
    else:
        list_versions_cmd(offline, output_json)

@app.command()
def info():
    """Print information about the current Ribbon configuration."""
    table = Table(title="Current Ribbon Configuration", show_header=False)
    table.add_row("Ribbon home directory", str(RIBBON_HOME))
    table.add_row("Config file", str(CONFIG_FILE))
    table.add_row("Cache directory", str(CACHE_DIR))
    table.add_row("Container directory", str(CONTAINER_DIR))
    table.add_row("Tasks directory", str(TASKS_DIR))
    table.add_row("GitHub API URL", str(GITHUB_API_URL))
    table.add_row("Active tasks version", str(TASKS_VERSION))
    console.print(table)

@app.command()
def use(tag: str = typer.Argument(..., help="GitHub release tag to use.")):
    """Set the active task version. Use [i]'ribbon list'[/i] to see available versions."""
    # Open the config file TOML and update the tasks_version:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # fallback for older Python versions
        except ImportError:
            console.print("[red]Error: No TOML library available for reading config.[/red]")
            raise typer.Exit(code=1)
    
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'rb') as f:
                config = tomllib.load(f)
        except Exception as e:
            console.print(f"[red]Error reading config file: {e}[/red]")
            raise typer.Exit(code=1)

    # Check if the tag exists in the releases
    remote_release_tags = [release['tag_name'] for release in fetch_remote_releases()]
    local_release_tags = fetch_local_releases()
    if not any(release_tag == tag for release_tag in remote_release_tags + local_release_tags):
        console.print(f"\n[red]Error: Tag '{tag}' not found in available releases.[/red]\n")
        # We can call the list command logic here:
        list_versions_cmd()
        raise typer.Exit(code=1)

    config["tasks_version"] = tag
    write_config_file(CONFIG_FILE, config)

    # Re-import ribbon, so the new tasks_version is loaded:
    try:
        import ribbon
        ribbon.initialize()
        console.print("[green]Successfully reloaded Ribbon with new tasks version.[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not reload Ribbon tasks: {e}[/yellow]")
        console.print("You may need to restart your Python session for changes to take effect.")

    console.print(f"Set active Ribbon-Tasks version to: [bold]{tag}[/bold]")

@app.command(name="deserialize-and-run", hidden=True)
def deserialize_and_run_cmd(file: str = typer.Argument(..., help="Path to the file containing the task definition.")):
    """Deserialize and run a Ribbon task definition from a file."""
    from ribbon import deserialize

    if not os.path.exists(file):
        console.print(f"[red]Error: File '{file}' does not exist.[/red]")
        raise typer.Exit(code=1)

    task = deserialize(file)
    task.run()

### TASK SUBCOMMAND HELPERS ###
def _normalize_task_name(name):
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())

def _to_kebab_case(name):
    """Convert CamelCase to kebab-case, handling digits."""
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name or "")
    s2 = re.sub('([a-zA-Z])([0-9])', r'\1-\2', s1)
    return s2.lower().replace("_", "-")

def _load_task_metadata(version=None):
    target_version = version or TASKS_VERSION
    tasks, _ = _load_tasks_file(target_version)
    return tasks or {}

def _discover_task_classes():
    import ribbon
    from ribbon.runner import Task as BaseTask

    discovered = {}
    for attr_name in dir(ribbon):
        attr = getattr(ribbon, attr_name)
        if not inspect.isclass(attr):
            continue
        if attr is BaseTask:
            continue
        if not issubclass(attr, BaseTask):
            continue
        if not attr.__module__.startswith("ribbon_tasks"):
            continue
        discovered[attr.__name__] = attr

    return discovered

def _build_task_registry(version=None):
    task_classes = _discover_task_classes()
    metadata = _load_task_metadata(version=version)

    registry = {}
    aliases = {}

    for class_name, task_class in task_classes.items():
        normalized_class = _normalize_task_name(class_name)
        matched_task_name = None
        for task_name in metadata.keys():
            if _normalize_task_name(task_name) == normalized_class:
                matched_task_name = task_name
                break

        display_name = matched_task_name or class_name
        description = metadata.get(display_name, {}).get("description", task_class.__doc__ or "")

        entry = {
            "class": task_class,
            "class_name": class_name,
            "task_name": matched_task_name,
            "display_name": display_name,
            "description": description.strip() if isinstance(description, str) else "",
        }
        registry[class_name] = entry

        for alias in (class_name, display_name, normalized_class):
            key = _normalize_task_name(alias)
            if key and key not in aliases:
                aliases[key] = class_name

    return registry, aliases

def _infer_arg_type(parameter):
    annotation = parameter.annotation
    default = parameter.default

    # Handle Optional[...] / Union[...] / List[...]
    if hasattr(annotation, "__origin__"):
        origin = annotation.__origin__
        
        # 1. Direct List types
        if origin is list or origin is List:
            return List[str]
            
        # 2. Union types (includes Optional)
        # Check for both typing.Union and types.UnionType (| operator in 3.10+)
        if str(origin).endswith('Union') or (hasattr(origin, '__name__') and 'Union' in origin.__name__):
            args = getattr(annotation, "__args__", [])
            # Search for List inside Union
            for arg in args:
                if (hasattr(arg, "__origin__") and (arg.__origin__ is list or arg.__origin__ is List)) or arg is list or arg is List:
                    return List[str]
            
            if args:
                # Pick the first non-None type for scalar types
                for arg in args:
                    if arg is not type(None):
                        annotation = arg
                        break

    if annotation in (int, float, str, bool):
        return annotation
    
    if annotation is list or annotation is List:
        return List[str]

    if default is not inspect._empty and default is not None:
        if type(default) in (int, float, str, bool):
            return type(default)
        if isinstance(default, list):
            return List[str]
            
    return str


def _register_dynamic_tasks(target_app: typer.Typer):
    """Dynamically register discovered tasks as subcommands in the target Typer app."""
    registry, _ = _build_task_registry()
    
    for class_name, entry in registry.items():
        task_class = entry["class"]
        description = entry["description"]
        kebab_name = _to_kebab_case(class_name)
        normalized_name = _normalize_task_name(class_name)

        # Build dynamic signature from __init__
        init_sig = inspect.signature(task_class.__init__)
        params = []
        
        for name, param in init_sig.parameters.items():
            if name == "self":
                continue
            
            arg_type = _infer_arg_type(param)
            
            # Map Python default to Typer's Argument/Option
            if param.default is inspect.Parameter.empty:
                # Required argument
                default_val = typer.Argument(..., help=f"Required argument: {name}")
            else:
                # Optional with default
                default_val = typer.Option(param.default, help=f"Default: {param.default}")
            
            params.append(inspect.Parameter(
                name=name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default_val,
                annotation=arg_type
            ))
            
        # Create a wrapper function that Typer can inspect
        def create_task_wrapper(t_class):
            def task_wrapper(**kwargs):
                task = t_class(**kwargs)
                task.run()
            return task_wrapper

        wrapper = create_task_wrapper(task_class)
        wrapper.__doc__ = description
        wrapper.__signature__ = inspect.Signature(params)

        # Register the primary CamelCase command
        target_app.command(name=class_name)(wrapper)
        
        # Register aliases: kebab-case and lowercase
        aliases_to_add = set()
        if kebab_name != class_name:
            aliases_to_add.add(kebab_name)
        
        if normalized_name != class_name and normalized_name != kebab_name:
            aliases_to_add.add(normalized_name)

        for alias in aliases_to_add:
            target_app.command(name=alias, hidden=True)(wrapper)


@run_app.callback(invoke_without_command=True)
def run_callback(
    ctx: typer.Context,
    list_runnable: bool = typer.Option(False, "--list", help="List runnable tasks.")
):
    """Run a task from the active Ribbon-Tasks module."""
    if list_runnable:
        registry, _ = _build_task_registry()
        if not registry:
            console.print("[yellow]No runnable tasks discovered in the active Ribbon-Tasks version.[/yellow]")
            return
        
        table = Table(title="Runnable Tasks", box=None, show_header=False, padding=(0, 2))
        table.add_column("Task", style="cyan")
        table.add_column("Alias", style="dim")
        for entry in sorted(registry.values(), key=lambda item: item["display_name"].lower()):
            table.add_row(f"- {entry['display_name']}", f"({entry['class_name']})")
        console.print(table)
        raise typer.Exit()

def main():
    _register_dynamic_tasks(run_app)
    app.add_typer(run_app, name="run")
    app()

if __name__ == "__main__":
    main()
