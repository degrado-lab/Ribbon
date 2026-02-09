# ribbon/cli.py
import json
import os
import argparse
import urllib
import re
import inspect
import copy
from datetime import datetime

from ribbon.config import RIBBON_HOME, CONFIG_FILE, CACHE_DIR, TASKS_DIR, CONTAINER_DIR, GITHUB_API_URL, TASKS_VERSION
from ribbon.config.parse_config import write_config_file

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
                    print(f"Warning: Could not fetch online releases (HTTP {response.getcode()}).")
                return []
    except urllib.error.URLError as e:
        if not quiet:
            print(f"Warning: Could not fetch online releases: {e}")
        return []
    except json.JSONDecodeError as e:
        if not quiet:
            print(f"Warning: Could not parse online releases response: {e}")
        return []

def fetch_local_releases():
    """Fetch local releases from the cache directory."""
    local_releases = [item.name for item in TASKS_DIR.iterdir() if item.is_dir()]
    return sorted(local_releases, key=_version_sort_key, reverse=True)

def _load_tasks_file(version):
    tasks_file = TASKS_DIR / version / "Ribbon-Tasks" / "ribbon_tasks" / "tasks.json"
    if not tasks_file.exists():
        return None, tasks_file

    try:
        with open(tasks_file) as f:
            return json.load(f), tasks_file
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in task definition file '{tasks_file}': {e}")
        return None, tasks_file
    except Exception as e:
        print(f"Error reading task definition file '{tasks_file}': {e}")
        return None, tasks_file

def _extract_inputs_from_command(command):
    seen = set()
    ordered_inputs = []
    for match in re.findall(r"\{([^{}]+)\}", command or ""):
        if match not in seen:
            seen.add(match)
            ordered_inputs.append(match)
    return ordered_inputs

def list_versions(include_remote=True, output_json=False):
    """List available Ribbon-Tasks versions."""
    releases = fetch_remote_releases(quiet=output_json) if include_remote else []
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
        print(json.dumps(output, indent=2))
        return

    if include_remote:
        if releases:
            print("\nOfficial Releases:   (Released)")
            for release in releases:
                tag = release.get("tag_name", "Unknown")
                published = release.get("published_at", "Unknown date")
                active = "*" if tag == TASKS_VERSION else " "
                print(f"{active}  {tag:<15} - {published[:10]}")
        else:
            print("\nOfficial Releases:   (Released)")
            print("Unavailable (offline or API error).")

    print("\nCustom Releases:     (Modified)")
    if not local_releases:
        print("No local versions found.")
    else:
        for tag in local_releases:
            active = "*" if tag == TASKS_VERSION else " "
            modified_date = datetime.fromtimestamp((TASKS_DIR / tag).stat().st_mtime).strftime("%Y-%m-%d")
            print(f"{active}  {tag:<15} - {modified_date}")

    print("")

def list_task_definitions(version=None, verbose=False, output_json=False):
    """List tasks for a Ribbon-Tasks version (defaults to active)."""
    target_version = version or TASKS_VERSION
    tasks, tasks_file = _load_tasks_file(target_version)

    if tasks is None:
        print(f"Error: Could not load tasks for version '{target_version}'.")
        print(f"Expected task definition file: {tasks_file}")
        return

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
        print(json.dumps(payload, indent=2))
        return

    version_label = " (active)" if target_version == TASKS_VERSION else ""
    print(f"\nTasks in Ribbon-Tasks {target_version}{version_label}:")
    if not task_names:
        print("No tasks found.")
        print("")
        return

    if not verbose:
        for task_name in task_names:
            print(f"- {task_name}")
    else:
        for task_name in task_names:
            task = tasks.get(task_name, {})
            inputs = _extract_inputs_from_command(task.get("command", ""))
            print(f"- {task_name}")
            print(f"  description: {task.get('description', 'N/A')}")
            print(f"  container:   {task.get('container', 'N/A')}")
            print(f"  inputs:      {', '.join(inputs) if inputs else '(none)'}")
            print("")
        return

    print("")

# Backward-compatible alias for existing imports/usages.
def list_tasks():
    list_versions()

def use(tag):
    """Set the active task version."""
    # Open the config file TOML and update the tasks_version:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # fallback for older Python versions
        except ImportError:
            print("Error: No TOML library available for reading config.")
            return
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'rb') as f:
                config = tomllib.load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            return

    # Check if the tag exists in the releases
    remote_release_tags = [release['tag_name'] for release in fetch_remote_releases()]
    local_release_tags = fetch_local_releases()
    if not any(release_tag == tag for release_tag in remote_release_tags + local_release_tags):
        print(f"\nError: Tag '{tag}' not found in available releases.\n")
        list_versions()
        return

    config["tasks_version"] = tag

    write_config_file(CONFIG_FILE, config)

    # Re-import ribbon, so the new tasks_version is loaded:
    try:
        import ribbon
        ribbon.initialize()
        print("Successfully reloaded Ribbon with new tasks version.")
    except Exception as e:
        print(f"Warning: Could not reload Ribbon tasks: {e}")
        print("You may need to restart your Python session for changes to take effect.")

    print(f"Set active Ribbon-Tasks version to: {tag}")

def info():
    """Print information about the current Ribbon configuration."""
    print(f"Current Ribbon configuration:")
    print(f"  Ribbon home directory: \t{RIBBON_HOME}")
    print(f"  Config file: \t\t\t{CONFIG_FILE}")
    print(f"  Cache directory: \t\t{CACHE_DIR}")
    print(f"  Container directory: \t\t{CONTAINER_DIR}")
    print(f"  Tasks directory: \t\t{TASKS_DIR}")
    print(f"  GitHub API URL: \t\t{GITHUB_API_URL}")
    print(f"  Active tasks version: \t{TASKS_VERSION}")

def deserialize_and_run(file):
    """Deserialize and run a Ribbon task definition from a file."""
    from ribbon import deserialize

    if not os.path.exists(file):
        print(f"Error: File '{file}' does not exist.")
        return

    # Deserialize the task:
    task = deserialize(file)

    # Run the task:
    task.run()


def _normalize_task_name(name):
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


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

    if annotation in (int, float, str):
        return annotation
    if default is not inspect._empty and default is not None:
        if type(default) in (int, float, str):
            return type(default)
    return str


def _build_task_arg_parser(entry):
    class_name = entry["class_name"]
    display_name = entry["display_name"]
    description = entry["description"]
    task_class = entry["class"]

    parser = argparse.ArgumentParser(
        prog=f"ribbon run {class_name}",
        description=(description or f"Run {display_name}."),
    )

    signature = inspect.signature(task_class.__init__)
    params = []

    for param_name, parameter in signature.parameters.items():
        if param_name == "self":
            continue
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        params.append((param_name, parameter))
        cli_name = param_name.replace("_", "-")

        if parameter.default is inspect._empty:
            parser.add_argument(param_name, type=_infer_arg_type(parameter))
            continue

        default = parameter.default

        if isinstance(default, bool):
            if default:
                parser.add_argument(
                    f"--no-{cli_name}",
                    dest=param_name,
                    action="store_false",
                    default=True,
                    help=f"Disable {param_name} (default: enabled).",
                )
            else:
                parser.add_argument(
                    f"--{cli_name}",
                    dest=param_name,
                    action="store_true",
                    default=False,
                    help=f"Enable {param_name} (default: disabled).",
                )
            continue

        if isinstance(default, list):
            parser.add_argument(
                f"--{cli_name}",
                dest=param_name,
                action="append",
                default=None,
                type=_infer_arg_type(parameter),
                help=(
                    f"Repeat to add multiple values. "
                    f"Default: {default}"
                ),
            )
            continue

        parser.add_argument(
            f"--{cli_name}",
            dest=param_name,
            default=default,
            type=_infer_arg_type(parameter),
            help=f"Default: {default}",
        )

    return parser, params


def _print_run_help(run_parser, registry):
    run_parser.print_help()
    if registry:
        print("\nAvailable tasks:")
        for entry in sorted(registry.values(), key=lambda item: item["display_name"].lower()):
            display = entry["display_name"]
            class_name = entry["class_name"]
            desc = entry["description"] or "No description provided."
            print(f"- {class_name}")
            print(f"    {desc}")


def run_task(task_name, task_args, list_only=False, show_run_help=False):
    '''
    Create an instance of the CLI-specified task, and run it locally.
    '''
    registry, aliases = _build_task_registry()

    if list_only:
        if not registry:
            print("No runnable tasks discovered in the active Ribbon-Tasks version.")
            return
        print("\nRunnable tasks:")
        for entry in sorted(registry.values(), key=lambda item: item["display_name"].lower()):
            print(f"- {entry['display_name']} (alias: {entry['class_name']})")
        print("")
        return

    if show_run_help and not task_name:
        parser = argparse.ArgumentParser(
            prog="ribbon run",
            description="Run a Ribbon task from the active Ribbon-Tasks module.",
        )
        parser.add_argument("task", nargs="?", help="Task name or alias.")
        parser.add_argument("--list", action="store_true", help="List runnable tasks.")
        _print_run_help(parser, registry)
        return

    if not task_name:
        print("Error: Missing task name. Use `ribbon run --list` to see available tasks.")
        return

    normalized = _normalize_task_name(task_name)
    class_name = aliases.get(normalized)
    if class_name is None:
        print(f"Error: Unknown task '{task_name}'. Use `ribbon run --list` to see available tasks.")
        return

    entry = registry[class_name]
    parser, params = _build_task_arg_parser(entry)

    if show_run_help:
        parser.print_help()
        return

    parsed = parser.parse_args(task_args)

    kwargs = {}
    for param_name, parameter in params:
        value = getattr(parsed, param_name)
        if isinstance(parameter.default, list) and value is None:
            value = copy.copy(parameter.default)
        kwargs[param_name] = value

    task_instance = entry["class"](**kwargs)
    task_instance.run()

def main():
    parser = argparse.ArgumentParser(description="Manage Ribbon task definitions.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List Ribbon-Tasks versions (default) or task definitions."
    )
    list_parser.add_argument(
        "target",
        nargs="?",
        default="versions",
        choices=["versions", "tasks"],
        help="What to list: versions or tasks."
    )
    list_parser.add_argument(
        "--version",
        dest="tasks_version",
        type=str,
        help="Ribbon-Tasks version for `list tasks` (defaults to active version)."
    )
    list_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show task details (description, container, inputs) for `list tasks`."
    )
    list_parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip online release lookup for `list versions`."
    )
    list_parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output results as JSON."
    )

    # Use command
    use_parser = subparsers.add_parser("use", help="Set the active task version.")
    use_parser.add_argument("tag", type=str, help="GitHub release tag to use.")

    # Info command
    info_parser = subparsers.add_parser("info", help="Print information about the current Ribbon configuration.")

    # Deserialize and run command:
    deserialize_parser = subparsers.add_parser("deserialize_and_run", help="Deserialize and run a Ribbon task definition from a file (Used internally when queuing tasks).")
    deserialize_parser.add_argument("file", type=str, help="Path to the file containing the task definition.")

    # Run command:
    run_parser = subparsers.add_parser(
        "run",
        add_help=False,
        help="Run a task from the active Ribbon-Tasks module.",
    )
    run_parser.add_argument("task", nargs="?", help="Task name or alias.")
    run_parser.add_argument("--list", action="store_true", help="List runnable tasks.")
    run_parser.add_argument("-h", "--help", dest="run_help", action="store_true", help="Show help for `ribbon run` or a specific task.")

    args, unknown = parser.parse_known_args()

    if args.command != "run" and unknown:
        parser.error(f"unrecognized arguments: {' '.join(unknown)}")

    if args.command == "list":
        target = args.target
        # Convenience: `ribbon list --version vX.Y.Z` implies listing tasks.
        if args.tasks_version and args.target == "versions":
            target = "tasks"

        if target == "versions":
            list_versions(include_remote=not args.offline, output_json=args.output_json)
        else:
            list_task_definitions(
                version=args.tasks_version,
                verbose=args.verbose,
                output_json=args.output_json,
            )
    elif args.command == "use":
        use(args.tag)
    elif args.command == "info":
        info()
    elif args.command == "deserialize_and_run":
        deserialize_and_run(args.file)
    elif args.command == "run":
        run_task(
            task_name=args.task,
            task_args=unknown,
            list_only=args.list,
            show_run_help=getattr(args, "run_help", False),
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
