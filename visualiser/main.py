"""visualiser.refactored.main module.

Entry point for the refactored visualiser.

Usage:
    python3 -m visualiser.refactored.main config.txt
"""
import sys

from config.parser import load_config
from visualiser.refactored.app import App


def main() -> None:
    """Parse the config and run the visualiser."""
    if len(sys.argv[1:]) != 1:
        print("No config file given")
        print("Usage: python3 -m visualiser.refactored.main config.txt")
        sys.exit(0)

    config = load_config(sys.argv[1])
    App(config).run()


if __name__ == "__main__":
    main()
