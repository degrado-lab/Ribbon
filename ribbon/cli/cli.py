# ribbon/cli.py
import json
import os
from pathlib import Path
import argparse
import urllib

from ribbon.config import CONFIG_FILE, CACHE_DIR, TASKS_DIR, GITHUB_API_URL, TASKS_VERSION
from ribbon.config.parse_config import write_config_file

def fetch_remote_releases():
    """Fetch available releases from GitHub API using urllib."""
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen(GITHUB_API_URL) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                return data
            else:
                print(f"Error: HTTP {response.getcode()}")
                return []
    except urllib.error.URLError as e:
        print(f"Error fetching online releases: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def fetch_local_releases():
    """Fetch local releases from the cache directory."""
    local_releases = []
    for item in TASKS_DIR.iterdir():
        if item.is_dir():
            local_releases.append(item.name)
    return local_releases

def list_tasks():
    """List all available Ribbon-Tasks versions."""
    # Remote releases:
    releases = fetch_remote_releases()

    if releases:
        print("\nOfficial Releases:   (Released)")
        for release in releases:
            tag = release.get('tag_name', 'Unknown')
            published = release.get('published_at', 'Unknown date')
            active = "*" if tag == TASKS_VERSION else " "
            print(f"{active}  {tag:<15} - {published[:10]}")

    # Local versions:
    print("\nCustom Releases:     (Modified)")
    local_releases = fetch_local_releases()
    # Cull the local releases that match the remote releases:
    local_releases = [tag for tag in local_releases if tag not in [release['tag_name'] for release in releases]]
    if not local_releases:
        print("No local versions found.")
    else:
        for tag in local_releases:
            active = "*" if tag == TASKS_VERSION else " "
            # Get modified date:
            modified_timestamp = (TASKS_DIR / tag).stat().st_mtime
            modified_date_str = __import__('datetime').datetime.fromtimestamp(modified_timestamp).strftime('%Y-%m-%d')
            print(f"{active}  {tag:<15} - {modified_date_str}")
            #print(f"{active}  {tag}")

    print("")

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
        list_tasks()
        return

    config["tasks_version"] = tag

    write_config_file(CONFIG_FILE, config)

    # Re-import ribbon, so the new tasks_version is loaded:
    import importlib
    import ribbon
    importlib.reload(ribbon)

    print(f"Set active Ribbon-Tasks version to: {tag}")

def info():
    """Print information about the current Ribbon configuration."""
    print(f"Current Ribbon configuration:")
    print(f"  Config file: {CONFIG_FILE}")
    print(f"  Cache directory: {CACHE_DIR}")
    print(f"  GitHub API URL: {GITHUB_API_URL}")
    print(f"  Active tasks version: {TASKS_VERSION}")

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

    # Info command
    info_parser = subparsers.add_parser("info", help="Print information about the current Ribbon configuration.")

    args = parser.parse_args()
    
    if args.command == "install":
        install(args.tag)
    elif args.command == "list":
        list_tasks()
    elif args.command == "use":
        use(args.tag)
    elif args.command == "info":
        info()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
