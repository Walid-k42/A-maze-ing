#!/usr/bin/env python3

import sys
import os
import tty
import termios
from typing import Any, Annotated
from pydantic import BaseModel, Field, model_validator, field_validator
from pydantic import ValidationError

from mazegen import MazeTester
from config_parser import MazeConfig, read_and_split


def get_single_key() -> str:

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


def main() -> None:

    if len(sys.argv) != 2:
        print("Error: Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    filename = sys.argv[1]
    valid_data = read_and_split(filename)

    if not valid_data:
        return

    try:
        config = MazeConfig(**valid_data)
        tester = MazeTester(config.width, config.height)

        grid = tester._init_ascii_grid()

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            if grid:
                for row in grid:
                    print("".join(row))

            print("\n --- MENU ---")
            print("[R] Regenerate the Maze")
            print("[S] Test a seed")
            print("[Q] Quit")

            choice = get_single_key().lower()

            if choice == 'q':
                print("Closing the maze...")
                break

            elif choice == 'r':
                grid = tester._init_ascii_grid()
            
            elif choice == 's':
                seed_user = input("\n Enter your seed and press [Enter]")

            else:
                pass

    except ValidationError as e:
        clean_msg = e.errors()[0]['msg'].replace("Value error, ", "")
        print(f"Error: {clean_msg}")


if __name__ == "__main__":
    main()
