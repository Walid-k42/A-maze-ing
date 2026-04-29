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
COLOR_PATH = '\033[94m'
COLOR_START = '\033[92m'
COLOR_EXIT = '\033[91m'

THEMES = [
    {"name": "Ghost", "wall": "\033[90m", "pattern": "\033[97m", "menu":
     "\033[90m"},
    {"name": "Barca", "wall": "\033[34m", "pattern": "\033[31m", "menu":
     "\033[93m"},
    {"name": "Cyberpunk", "wall": "\033[95m", "pattern": "\033[96m", "menu":
     "\033[95m"},
    {"name": "Hell", "wall": "\033[93m", "pattern": "\033[91m", "menu":
     "\033[31m"},
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


def apply_solution(grid: list[list[str]], tester: MazeTester) -> None:
    path = tester.solve()
    for cell in path:
        cx, cy = cell["x"] * 2 + 1, cell["y"] * 2 + 1
        if grid[cy][cx] == "  ":
            grid[cy][cx] = "o "


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    valid_data = read_and_split(sys.argv[1])
    if not valid_data:
        return

    try:
        config = MazeConfig(**valid_data)
        tester = MazeTester(config.width, config.height, list(config.entry),
                            list(config.exit), is_perfect=config.perfect)

        show_solution = False
        theme_index = 0
        theme = THEMES[theme_index]
        use_animation = True

        tester.wall_char = f"{theme['wall']}██{COLOR_RESET}"
        tester.pattern_char = f"{theme['pattern']}▓▓{COLOR_RESET}"

        current_seed = random.randint(1, 999999)
        tester.generate(seed=current_seed, animate=use_animation)

        tester.export_to_hex(config.output_file)

        grid = tester.init_ascii_grid()
        tester.apply_walls_to_ascii(grid)

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            theme = THEMES[theme_index]
            print(f"{theme['menu']}{TITLE}{COLOR_RESET}")

            if grid:
                for row in grid:
                    line = "".join(row).replace("o ", f"{COLOR_PATH}██{COLOR_RESET}") \
                                    .replace("START ", f"{COLOR_START}██{COLOR_RESET}") \
                                    .replace("END ", f"{COLOR_EXIT}██{COLOR_RESET}")
                    print(line)

            status_anim = "ON" if use_animation else "OFF"
            print(f"\n{theme['menu']} --- MENU (Seed: {current_seed} | Theme: "
                  f"{theme['name']} | Anim: {status_anim}) ---{COLOR_RESET}")
            print(f"{theme['menu']}[R] Regenerate | [S] Seed | [C] Color "
                  f"|[A] Anim | [H] Solve | [Q] Quit{COLOR_RESET}")

            choice = get_single_key().lower()

            if choice == 'q':
                break
            elif choice == 'c':
                theme_index = (theme_index + 1) % len(THEMES)
                theme = THEMES[theme_index] 

                tester.wall_char = f"{theme['wall']}██{COLOR_RESET}"
                tester.pattern_char = f"{theme['pattern']}▓▓{COLOR_RESET}"

                grid = tester.init_ascii_grid()
                tester.apply_walls_to_ascii(grid)
                if show_solution:
                    apply_solution(grid, tester)
            elif choice == 'h':
                show_solution = not show_solution
                grid = tester.init_ascii_grid()
                tester.apply_walls_to_ascii(grid)
                if show_solution:
                    apply_solution(grid, tester)
            elif choice == 'a':
                use_animation = not use_animation
            elif choice == 'r' or choice == 's':
                if choice == 'r':
                    current_seed = random.randint(1, 999999)
                else:
                    s_input = input(f"\n{theme['menu']} Seed: {COLOR_RESET}").strip()
                    current_seed = int(s_input) if s_input.isdigit() else current_seed
                theme = THEMES[theme_index]

                tester = MazeTester(config.width, config.height,
                                    list(config.entry), list(config.exit),
                                    is_perfect=config.perfect)

                tester.wall_char = f"{theme['wall']}██{COLOR_RESET}"
                tester.pattern_char = f"{theme['pattern']}▓▓{COLOR_RESET}"

                tester.generate(seed=current_seed, animate=use_animation)

                tester.export_to_hex(config.output_file)

                grid = tester.init_ascii_grid()
                tester.apply_walls_to_ascii(grid)
                if show_solution:
                    apply_solution(grid, tester)

    except ValidationError as e:
        clean_msg = e.errors()[0]['msg'].replace("Value error, ", "")
        print(f"Error: {clean_msg}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
