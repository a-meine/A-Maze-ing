#!/usr/bin/env python3

import sys
from config.parser import load_config
from visualiser.mlx_visualiser import Window


if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print("No config file were given")
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(0)

    config_file: str = sys.argv[1]
    try:
        config = load_config(config_file)
        print("parsed config parameters: ")
        # print(maze_config)
    except (KeyError, ValueError, TypeError) as e:
        print(e)
        exit(1)
    Window().run()
