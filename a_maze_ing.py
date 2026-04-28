import sys
import tty
import termios
import os
import random
from pydantic import ValidationError
from mazegen import MazeTester
from config_parser import MazeConfig, read_and_split

TITLE = r"""
    ___           __  ___                     _            
   /   |         /  |/  /____ _ ____ ___     (_)____   ____ _
  / /| | ______ / /|_/ // __ `//_  // _ \ ______/ // __ \ / __ `/
 / ___ |/_____// /  / // /_/ /  / //  __//_____/ / / / // /_/ / 
/_/  |_|      /_/  /_/ \__,_/  /___/\___/     /_/_/ /_/\__, /  
                                                      /____/   
"""

COLOR_RESET = '\033[0m'

THEMES = [
    {"name": "VSCode", "wall": "\033[94m", "pattern": "\033[92m", "menu": "\033[93m"},
    {"name": "Matrix", "wall": "\033[32m", "pattern": "\033[92m", "menu": "\033[32m"},
    {"name": "Cyberpunk", "wall": "\033[95m", "pattern": "\033[96m", "menu": "\033[93m"},
    {"name": "Hell", "wall": "\033[91m", "pattern": "\033[93m", "menu": "\033[31m"},
]


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

        tester = MazeTester(config.width, config.height, config.entry,
                            config.exit)

        current_seed = random.randint(1, 999999)
        tester.generate(seed=current_seed)
        grid = tester.init_ascii_grid()
        tester.apply_walls_to_ascii(grid)

        theme_index = 0

        while True:

            os.system('cls' if os.name == 'nt' else 'clear')

            theme = THEMES[theme_index]

            print(f"{theme['menu']}{TITLE}{COLOR_RESET}")

            if grid:
                for row in grid:
                    line = "".join(row)
                    line = line.replace("█", f"{theme['wall']}█{COLOR_RESET}")
                    line = line.replace("▓", f"{theme['pattern']}▓{COLOR_RESET}")
                    print(line)

            print(f"Seed: {current_seed}")
            if config.width < 7 or config.height < 5:
                print(" [!] Warning: The maze is too small to "
                      "display the '42' pattern.")
            print("\n --- MENU ---")
            print("[R] Regenerate")
            print("[S] Enter a seed")
            print("[Q] Quit")

            choice = get_single_key().lower()

            if choice == 'q':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Closing the maze...")
                break

            elif choice == 'r':
                current_seed = random.randint(1, 999999)
                tester = MazeTester(config.width, config.height, config.entry,
                                    config.exit)
                tester.generate(seed=current_seed)
                grid = tester.init_ascii_grid()
                tester.apply_walls_to_ascii(grid)

            elif choice == 's':
                seed_u = input("\n Enter your seed and press [Enter]").strip()

                if seed_u.isdigit():
                    current_seed = int(seed_u)
                    tester = MazeTester(config.width, config.height,
                                        config.entry, config.exit)
                    tester.generate(seed=current_seed)
                    grid = tester.init_ascii_grid()
                    tester.apply_walls_to_ascii(grid)

                else:
                    print(" Invalid seed. Please enter a positive number.")

    except ValidationError as e:
        clean_msg = e.errors()[0]['msg'].replace("Value error, ", "")
        print(f"Error: {clean_msg}")
    except IndexError:
        print("Error: Coordinates are out of bounds. Check your config file.")


if __name__ == "__main__":
    main()
