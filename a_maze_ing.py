"""
Main entry point for the A-Maze-ing project.
Handles the interactive terminal interface, real-time keypress capture,
and the visual ASCII rendering of the generated maze.
"""

import sys
import tty
import termios
import os
import random
from pydantic import ValidationError
from mazegen import MazeGenerator
from config_parser import MazeConfig, read_and_split


TITLE = r"""
    ___           __  ___                     _
   /   |         /  |/  /____ _ ____ ___     (_)____   ____ _
  / /| | ______ / /|_/ // __ `//_  // _ \ ______/ // __ \ / __ `/
 / ___ |/_____// /  / // /_/ /  / //  __//_____/ / / / // /_/ /
/_/  |_|      /_/  /_/ \__,_/  /___/\___/     /_/_/ /_/\__, /
                                                      /____/
"""

COLOR_RESET = "\033[0m"
COLOR_PATH = "\033[94m"
COLOR_START = "\033[92m"
COLOR_EXIT = "\033[91m"

THEMES = [
    {
        "name": "Ghost",
        "wall": "\033[90m",
        "pattern": "\033[97m",
        "menu": "\033[90m",
    },
    {
        "name": "Barca",
        "wall": "\033[34m",
        "pattern": "\033[31m",
        "menu": "\033[93m",
    },
    {
        "name": "Cyberpunk",
        "wall": "\033[95m",
        "pattern": "\033[96m",
        "menu": "\033[95m",
    },
    {
        "name": "Hell",
        "wall": "\033[93m",
        "pattern": "\033[91m",
        "menu": "\033[31m",
    },
]


class MenuState:
    """
    Stores and updates the interactive menu state.

    Attributes:
        config (MazeConfig): Validated maze configuration.
        theme_index (int): Current theme index.
        current_seed (int): Current maze generation seed.
        use_animation (bool): Whether animation is enabled.
        show_solution (bool): Whether the solution path is displayed.
        tester (MazeGenerator): Current maze generator instance.
        grid (list[list[str]]): Current ASCII grid.
    """

    def __init__(self, config: MazeConfig) -> None:
        """
        Initializes the menu state and generates the first maze.

        Args:
            config (MazeConfig): The validated maze configuration.
        """
        self.config = config
        self.theme_index = 0
        self.current_seed = get_initial_seed(config)
        self.use_animation = should_use_animation(config)
        self.show_solution = False

        self.tester, self.grid = regenerate_maze(
            self.config,
            self.get_theme(),
            self.current_seed,
            self.use_animation,
            self.show_solution,
        )

    def get_theme(self) -> dict[str, str]:
        """
        Gets the currently selected theme.

        Returns:
            dict[str, str]: The current theme.
        """
        return THEMES[self.theme_index]

    def change_theme(self) -> None:
        """
        Switches to the next visual theme and rebuilds the maze display.
        """
        self.theme_index = (self.theme_index + 1) % len(THEMES)

        apply_theme_to_tester(self.tester, self.get_theme())
        self.grid = rebuild_grid(self.tester, self.show_solution)

    def toggle_solution(self) -> None:
        """
        Shows or hides the shortest path solution.
        """
        self.show_solution = not self.show_solution
        self.grid = rebuild_grid(self.tester, self.show_solution)

    def toggle_animation(self) -> None:
        """
        Enables or disables maze generation animation.
        """
        self.use_animation = not self.use_animation

    def regenerate_with_random_seed(self) -> None:
        """
        Regenerates the maze with a new random seed.
        """
        self.current_seed = random.randint(1, 999999)
        self.regenerate_current_maze()

    def regenerate_with_custom_seed(self) -> None:
        """
        Asks the user for a seed and regenerates the maze with it.
        """
        self.current_seed = ask_for_seed(
            self.current_seed,
            self.get_theme(),
        )
        self.regenerate_current_maze()

    def regenerate_current_maze(self) -> None:
        """
        Regenerates the maze using the current state values.
        """
        self.tester, self.grid = regenerate_maze(
            self.config,
            self.get_theme(),
            self.current_seed,
            self.use_animation,
            self.show_solution,
        )


def get_single_key() -> str:
    """
    Captures a single key press without requiring the Enter key.

    Returns:
        str: The pressed character.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return key


def format_validation_error(error: ValidationError) -> str:
    """
    Converts a Pydantic validation error into a readable message.

    Args:
        error (ValidationError): Validation error raised by Pydantic.

    Returns:
        str: A clean error message for the user.
    """
    first_error = error.errors()[0]
    message = str(first_error.get("msg", "Invalid configuration"))
    message = message.replace("Value error, ", "")

    field_parts = first_error.get("loc", [])
    field = ".".join(str(part) for part in field_parts)

    if field:
        return f"{field}: {message}"

    return message


def load_config_from_args() -> MazeConfig | None:
    """
    Loads and validates the config file from command-line arguments.

    Returns:
        MazeConfig | None: Valid config, or None if an error occurred.
    """
    if len(sys.argv) != 2:
        print("Error: Usage: python3 a_maze_ing.py <config_file>")
        return None

    config_path = sys.argv[1]

    try:
        valid_data = read_and_split(config_path)

        if not valid_data:
            raise ValueError("Configuration file is empty")

        return MazeConfig(**valid_data)

    except ValidationError as error:
        print(f"Error: {format_validation_error(error)}")
    except ValueError as error:
        print(f"Error: {error}")
    except OSError as error:
        print(f"Error: Could not read config file. {error}")

    return None


def get_initial_seed(config: MazeConfig) -> int:
    """
    Gets the initial seed from the config or generates a random one.

    Args:
        config (MazeConfig): The validated maze configuration.

    Returns:
        int: The seed used to generate the maze.
    """
    if config.seed is not None:
        return config.seed

    return random.randint(1, 999999)


def should_use_animation(config: MazeConfig) -> bool:
    """
    Determines whether animation should be enabled by default.

    Args:
        config (MazeConfig): The validated maze configuration.

    Returns:
        bool: True if animation should be enabled, False otherwise.
    """
    return config.width <= 20 and config.height <= 20


def apply_theme_to_tester(
    tester: MazeGenerator,
    theme: dict[str, str],
) -> None:
    """
    Applies the selected theme colors to the maze tester.

    Args:
        tester (MazeGenerator): The maze generator instance.
        theme (dict[str, str]): The selected theme.
    """
    tester.wall_char = f"{theme['wall']}██{COLOR_RESET}"
    tester.pattern_char = f"{theme['pattern']}▓▓{COLOR_RESET}"


def create_tester(
    config: MazeConfig,
    theme: dict[str, str],
) -> MazeGenerator:
    """
    Creates a MazeGenerator instance from the configuration.

    Args:
        config (MazeConfig): The validated maze configuration.
        theme (dict[str, str]): The selected visual theme.

    Returns:
        MazeGenerator: A configured maze generator instance.
    """
    tester = MazeGenerator(
        config.width,
        config.height,
        list(config.entry),
        list(config.exit),
        is_perfect=config.perfect,
    )

    apply_theme_to_tester(tester, theme)

    return tester


def apply_solution(grid: list[list[str]], tester: MazeGenerator) -> None:
    """
    Applies the shortest path to the ASCII grid.

    Args:
        grid (list[list[str]]): The ASCII grid to modify.
        tester (MazeGenerator): The maze generator used to solve the maze.
    """
    path = tester.solve()

    for cell in path:
        cell_x = cell["x"] * 2 + 1
        cell_y = cell["y"] * 2 + 1

        if grid[cell_y][cell_x] == "  ":
            grid[cell_y][cell_x] = "o "


def rebuild_grid(
    tester: MazeGenerator,
    show_solution: bool,
) -> list[list[str]]:
    """
    Rebuilds the ASCII grid from the current maze structure.

    Args:
        tester (MazeGenerator): The current maze generator instance.
        show_solution (bool): Whether the solution path should be shown.

    Returns:
        list[list[str]]: The rebuilt ASCII grid.
    """
    grid = tester.init_ascii_grid()
    tester.apply_walls_to_ascii(grid)

    if show_solution:
        apply_solution(grid, tester)

    return grid


def generate_and_export(
    tester: MazeGenerator,
    config: MazeConfig,
    seed: int,
    use_animation: bool,
    show_solution: bool,
) -> list[list[str]]:
    """
    Generates the maze, exports it, and returns the ASCII grid.

    Args:
        tester (MazeGenerator): The maze generator instance.
        config (MazeConfig): The validated maze configuration.
        seed (int): The seed used for generation.
        use_animation (bool): Whether animation should be enabled.
        show_solution (bool): Whether the solution should be displayed.

    Returns:
        list[list[str]]: The generated ASCII grid.
    """
    tester.generate(seed=seed, animate=use_animation)
    tester.export_to_hex(config.output_file)

    return rebuild_grid(tester, show_solution)


def clear_terminal() -> None:
    """
    Clears the terminal screen.
    """
    os.system("cls" if os.name == "nt" else "clear")


def render_ascii_grid(grid: list[list[str]]) -> None:
    """
    Displays the ASCII grid with colors for special cells.

    Args:
        grid (list[list[str]]): The ASCII grid to display.
    """
    for row in grid:
        line = "".join(row)
        line = line.replace("o ", f"{COLOR_PATH}██{COLOR_RESET}")
        line = line.replace("START ", f"{COLOR_START}██{COLOR_RESET}")
        line = line.replace("END ", f"{COLOR_EXIT}██{COLOR_RESET}")

        print(line)


def render_menu(
    seed: int,
    theme: dict[str, str],
    use_animation: bool,
) -> None:
    """
    Displays the interactive menu.

    Args:
        seed (int): The current maze seed.
        theme (dict[str, str]): The selected visual theme.
        use_animation (bool): Whether animation is enabled.
    """
    status_anim = "ON" if use_animation else "OFF"

    print(
        f"\n{theme['menu']} --- MENU "
        f"(Seed: {seed} | Theme: {theme['name']} | "
        f"Anim: {status_anim}) ---{COLOR_RESET}"
    )

    print(
        f"{theme['menu']}"
        "[R] Regenerate | "
        "[S] Seed | "
        "[C] Color | "
        "[A] Anim | "
        "[H] Solve | "
        "[Q] Quit"
        f"{COLOR_RESET}"
    )


def render_screen(
    grid: list[list[str]],
    seed: int,
    theme: dict[str, str],
    use_animation: bool,
) -> None:
    """
    Renders the full terminal screen.

    Args:
        grid (list[list[str]]): The ASCII maze grid.
        seed (int): The current seed.
        theme (dict[str, str]): The selected visual theme.
        use_animation (bool): Whether animation is enabled.
    """
    clear_terminal()

    print(f"{theme['menu']}{TITLE}{COLOR_RESET}")
    render_ascii_grid(grid)
    render_menu(seed, theme, use_animation)


def ask_for_seed(
    current_seed: int,
    theme: dict[str, str],
) -> int:
    """
    Asks the user to enter a custom seed.

    Args:
        current_seed (int): The current seed used as fallback.
        theme (dict[str, str]): The selected visual theme.

    Returns:
        int: The new seed, or the current seed if input is invalid.
    """
    seed_input = input(f"\n{theme['menu']}Seed: {COLOR_RESET}").strip()

    if seed_input.isdigit():
        return int(seed_input)

    return current_seed


def regenerate_maze(
    config: MazeConfig,
    theme: dict[str, str],
    seed: int,
    use_animation: bool,
    show_solution: bool,
) -> tuple[MazeGenerator, list[list[str]]]:
    """
    Creates a new tester and regenerates the maze.

    Args:
        config (MazeConfig): The validated maze configuration.
        theme (dict[str, str]): The selected visual theme.
        seed (int): The seed used for generation.
        use_animation (bool): Whether animation should be enabled.
        show_solution (bool): Whether the solution should be shown.

    Returns:
        tuple[MazeGenerator, list[list[str]]]: New tester and ASCII grid.
    """
    tester = create_tester(config, theme)
    grid = generate_and_export(
        tester,
        config,
        seed,
        use_animation,
        show_solution,
    )

    return tester, grid


def handle_menu_choice(choice: str, state: MenuState) -> bool:
    """
    Handles one user menu choice.

    Args:
        choice (str): The key pressed by the user.
        state (MenuState): The current menu state.

    Returns:
        bool: False if the program should quit, True otherwise.
    """
    if choice == "q":
        return False

    if choice == "c":
        state.change_theme()
    elif choice == "h":
        state.toggle_solution()
    elif choice == "a":
        state.toggle_animation()
    elif choice == "r":
        state.regenerate_with_random_seed()
    elif choice == "s":
        state.regenerate_with_custom_seed()

    return True


def run_menu_loop(config: MazeConfig) -> None:
    """
    Runs the interactive terminal menu.

    Args:
        config (MazeConfig): The validated maze configuration.
    """
    state = MenuState(config)

    while True:
        render_screen(
            state.grid,
            state.current_seed,
            state.get_theme(),
            state.use_animation,
        )

        choice = get_single_key().lower()

        if not handle_menu_choice(choice, state):
            break


def main() -> None:
    """
    Program entry point.

    Loads the configuration and starts the interactive maze interface.
    """
    config = load_config_from_args()

    if config is None:
        return

    run_menu_loop(config)


if __name__ == "__main__":
    main()
