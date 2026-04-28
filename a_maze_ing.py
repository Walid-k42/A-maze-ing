import sys
import tty
import termios
import os
import random
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

        tester = MazeTester(config.width, config.height, config.entry,
                            config.exit)

        current_seed = random.randint(1, 999999)
        tester.generate(seed=current_seed)
        grid = tester.init_ascii_grid()
        tester.apply_walls_to_ascii(grid)

        while True:

            os.system('cls' if os.name == 'nt' else 'clear')

            if grid:
                for row in grid:
                    print("".join(row))

            print(f"Seed: {current_seed}")
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
