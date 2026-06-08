#!/usr/bin/env python3

import sys
from maze.config_parser import load_config


if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print("No config file were given")
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(0)

    config_file: str = sys.argv[1]
    try:
        Maze_config = load_config(config_file)
        print("parsed config parameters: ")
        print(Maze_config)
    except (KeyError, ValueError, TypeError) as e:
        print(e)

