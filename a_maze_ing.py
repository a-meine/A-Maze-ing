#!/usr/bin/env python3
"""Entry point for the a_maze_ing application.

Loads the configuration file and starts the visualiser window.
"""

import sys
from config.parser import load_config
# from visualiser.mlx_visualiser import Window
from visualiser.app import App


if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print("No config file were given")
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(0)

    config_file: str = sys.argv[1]
    try:
        config = load_config(config_file)
        print("parsed config parameters: ")
    except (KeyError, ValueError, TypeError) as e:
        print(e)
        exit(1)
    App(config).run()