# ribbon/cli.py
import json
import os
from pathlib import Path
import argparse
import urllib

from ribbon.config import CONFIG_FILE, TASK_CACHE_DIR, GITHUB_API_URL
from ribbon.config import write_config_file

def fetch_releases():
    """Fetch available releases from GitHub API using urllib."""
    try:
        with urllib.request.urlopen(GITHUB_API_URL) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                return data
            else:
                print(f"Error: HTTP {response.getcode()}")
                return []
    except urllib.error.URLError as e:
        print(f"Error fetching releases: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def list_tasks():
    """List all available Ribbon-Tasks versions."""
    print("Fetching available Ribbon-Tasks versions...")
    releases = fetch_releases()
    
    if not releases:
        print("No releases found or error occurred.")
        return
    
    print("\nAvailable versions:")
    for release in releases:
        tag = release.get('tag_name', 'Unknown')
        name = release.get('name', 'No name')
        published = release.get('published_at', 'Unknown date')
        prerelease = " (pre-release)" if release.get('prerelease', False) else ""
        print(f"  {tag:<15} - {name}{prerelease}")
        print(f"    Published: {published[:10]}")  # Just the date part

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

    config["tasks_version"] = tag

    write_config_file(CONFIG_FILE, config)

    print(f"Set active Ribbon-Tasks version to: {tag}")


def main():
    parser = argparse.ArgumentParser(description="Manage Ribbon task definitions.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a specific version of Ribbon tasks.")
    install_parser.add_argument("tag", type=str, default="latest", nargs="?", 
                               help="GitHub release tag to install (default: latest).")

    # List command
    list_parser = subparsers.add_parser("list", help="List all available Ribbon-Tasks versions.")

    # Use command
    use_parser = subparsers.add_parser("use", help="Set the active task version.")
    use_parser.add_argument("tag", type=str, help="GitHub release tag to use.")

    args = parser.parse_args()
    
    if args.command == "install":
        install(args.tag)
    elif args.command == "list":
        list_tasks()
    elif args.command == "use":
        use(args.tag)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
