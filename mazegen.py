from __future__ import annotations

import os
import random
from collections import deque
from time import sleep


class MazeGenerator:
    """
    Core class responsible for generating, solving, and exporting the maze.
    It implements an iterative DFS for generation and a BFS for solving,
    while ensuring a static '42' pattern is embedded in the center.
    """
    def __init__(
        self,
        width: int,
        height: int,
        entry: list[int],
        exit_p: list[int],
        is_perfect: bool = True,
    ) -> None:
        """
        Initializes the maze generator with the provided configuration.

        Args:
            width (int): The width of the maze in logical cells.
            height (int): The height of the maze in logical cells.
            entry (list[int]): Coordinates [x, y] of the starting point.
            exit_p (list[int]): Coordinates [x, y] of the exit point.
            is_perfect (bool): If True, generates a perfect maze (no loops).
                               If False, breaks additional walls.
                               Defaults to True.
        """
        self.width = width
        self.height = height
        self.entry_x = entry[0]
        self.entry_y = entry[1]
        self.exit_x = exit_p[0]
        self.exit_y = exit_p[1]
        self.is_perfect = is_perfect
        self.wall_char = "██"
        self.pattern_char = "▓▓"

        self.grid = [
            [
                {"N": True, "E": True, "S": True, "W": True}
                for _ in range(width)
            ]
            for _ in range(height)
        ]

        self.pattern_cells: list[dict[str, int]] = []
        self.setup_42_pattern()

    def setup_42_pattern(self) -> None:
        """
        Calculates and stores the coordinates of the cells that make up
        the '42' pattern in the center of the maze.
        """
        pattern_width = 7
        pattern_height = 5
        safe_width = 11
        safe_height = 9

        if self.width < safe_width or self.height < safe_height:
            print("Error: Maze size is too small to display the '42' pattern.")
            sleep(2)
            return

        start_x = int((self.width - pattern_width) / 2)
        start_y = int((self.height - pattern_height) / 2)

        relative_coords = [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 0, "y": 2},
            {"x": 1, "y": 2},
            {"x": 2, "y": 0},
            {"x": 2, "y": 1},
            {"x": 2, "y": 2},
            {"x": 2, "y": 3},
            {"x": 2, "y": 4},
            {"x": 4, "y": 0},
            {"x": 5, "y": 0},
            {"x": 6, "y": 0},
            {"x": 6, "y": 1},
            {"x": 4, "y": 2},
            {"x": 5, "y": 2},
            {"x": 6, "y": 2},
            {"x": 4, "y": 3},
            {"x": 4, "y": 4},
            {"x": 5, "y": 4},
            {"x": 6, "y": 4},
        ]

        for coord in relative_coords:
            self.pattern_cells.append(
                {
                    "x": start_x + coord["x"],
                    "y": start_y + coord["y"],
                }
            )

    def is_pattern_cell(self, check_x: int, check_y: int) -> bool:
        """
        Checks if a given coordinate belongs to the '42' pattern.

        Args:
            check_x (int): The X coordinate to check.
            check_y (int): The Y coordinate to check.

        Returns:
            bool: True if the cell is part of the pattern, False otherwise.
        """
        for cell in self.pattern_cells:
            if cell["x"] == check_x and cell["y"] == check_y:
                return True

        return False

    def init_ascii_grid(self) -> list[list[str]]:
        """
        Initializes the visual representation of the maze using ASCII
        characters.
        The grid is scaled up to visually represent walls and paths.

        Returns:
            list[list[str]]: A 2D array representing the visual maze grid.
        """
        ascii_width = 2 * self.width + 1
        ascii_height = 2 * self.height + 1

        grid = [
            [self.wall_char for _ in range(ascii_width)]
            for _ in range(ascii_height)
        ]

        for y in range(self.height):
            for x in range(self.width):
                char_x = x * 2 + 1
                char_y = y * 2 + 1

                if x == self.entry_x and y == self.entry_y:
                    grid[char_y][char_x] = "START "
                elif x == self.exit_x and y == self.exit_y:
                    grid[char_y][char_x] = "END "
                elif self.is_pattern_cell(x, y):
                    grid[char_y][char_x] = self.pattern_char
                else:
                    grid[char_y][char_x] = "  "

        return grid

    def apply_walls_to_ascii(self, ascii_grid: list[list[str]]) -> None:
        """
        Modifies the visual ASCII grid by carving out paths based on
        the logical maze configuration (removing walls).

        Args:
            ascii_grid (list[list[str]]): The visual grid to be modified.
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.is_pattern_cell(x, y):
                    continue

                cell = self.grid[y][x]
                cx = x * 2 + 1
                cy = y * 2 + 1

                if not cell["N"]:
                    ascii_grid[cy - 1][cx] = "  "
                if not cell["E"]:
                    ascii_grid[cy][cx + 1] = "  "
                if not cell["S"]:
                    ascii_grid[cy + 1][cx] = "  "
                if not cell["W"]:
                    ascii_grid[cy][cx - 1] = "  "

    def generate(
        self,
        seed: int | None = None,
        animate: bool = False,
    ) -> None:
        """
        Generates the maze paths using an Iterative Depth-First Search (DFS).

        Args:
            seed (int | None): Random seed for reproducible generation.
            Defaults to None.
            animate (bool): If True, renders the maze step-by-step in the
            terminal. Defaults to False.
        """
        if seed is not None:
            random.seed(seed)

        stack = [{"x": self.entry_x, "y": self.entry_y}]
        visited = self._create_visited_grid()

        self._mark_pattern_cells_as_visited(visited)
        visited[self.entry_y][self.entry_x] = True

        if animate:
            self._clear_terminal()

        while stack:
            if animate:
                self._render_animation_frame()

            current = stack[-1]
            cx = current["x"]
            cy = current["y"]

            neighbors = self._get_generation_neighbors(cx, cy, visited)

            if neighbors:
                chosen = random.choice(neighbors)
                self._remove_wall_between_cells(cx, cy, chosen)

                nx = int(chosen["x"])
                ny = int(chosen["y"])

                visited[ny][nx] = True
                stack.append(
                    {
                        "x": nx,
                        "y": ny,
                    }
                )
            else:
                stack.pop()

        if not self.is_perfect:
            self.make_imperfect(chance=0.2, animate=animate)

    def solve(self) -> list[dict[str, int]]:
        """
        Solves the maze using a Breadth-First Search (BFS) to
        guarantee the shortest path.

        Returns:
            list[dict[str, int]]: A list of coordinates representing
            the path from entry to exit.
        """
        queue = deque([{"x": self.entry_x, "y": self.entry_y}])
        visited = self._create_visited_grid()
        parents: dict[tuple[int, int], tuple[int, int]] = {}

        visited[self.entry_y][self.entry_x] = True

        while queue:
            current = queue.popleft()
            cx = current["x"]
            cy = current["y"]

            if cx == self.exit_x and cy == self.exit_y:
                return self._reconstruct_path(parents)

            neighbors = self._get_accessible_neighbors(cx, cy, visited)

            for neighbor in neighbors:
                nx = neighbor["x"]
                ny = neighbor["y"]

                visited[ny][nx] = True
                parents[(nx, ny)] = (cx, cy)

                queue.append(
                    {
                        "x": nx,
                        "y": ny,
                    }
                )

        return []

    def make_imperfect(
        self,
        chance: float = 0.02,
        animate: bool = False,
    ) -> None:
        """
        Converts a perfect maze into an imperfect one by randomly
        knocking down extra walls.

        Args:
            chance (float): The probability of breaking a wall in a cell.
            Defaults to 0.02.
            animate (bool): If True, renders the process in the terminal.
            Defaults to False.
        """
        if animate:
            self._clear_terminal()

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.is_pattern_cell(x, y):
                    continue

                if random.random() < chance:
                    self._open_random_extra_wall(x, y)

                    if animate:
                        self._render_animation_frame()

    def export_to_hex(self, filename: str) -> None:
        """
        Exports the maze configuration, entry/exit points,
        and solution path
        to a text file using hexadecimal encoding for walls.

        Args:
            filename (str): The name of the output file.
        """
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for row in self.grid:
                    line_hex = ""

                    for cell in row:
                        value = self._cell_to_hex_value(cell)
                        line_hex += hex(value)[2:].upper()

                    file.write(line_hex + "\n")

                file.write("\n")
                file.write(f"{self.entry_x},{self.entry_y}\n")
                file.write(f"{self.exit_x},{self.exit_y}\n")

                path = self.solve()
                path_str = self._path_to_directions(path)

                file.write(path_str + "\n")

        except OSError as error:
            print(f"Warning: Could not save the hex file. {error}")

    def _create_visited_grid(self) -> list[list[bool]]:
        """
        Creates a 2D boolean grid initialized to False to track
        visited cells.

        Returns:
            list[list[bool]]: The initialized visited grid.
        """
        return [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _mark_pattern_cells_as_visited(
        self,
        visited: list[list[bool]],
    ) -> None:
        """
        Marks all cells belonging to the '42' pattern as visited
        so generation algorithms ignore them.

        Args:
            visited (list[list[bool]]): The tracking grid to modify.
        """
        for cell in self.pattern_cells:
            visited[cell["y"]][cell["x"]] = True

    def _get_directions(self) -> list[dict[str, int | str]]:
        """
        Returns the four cardinal directions and their respective opposites.

        Returns:
            list[dict[str, int | str]]: Directional deltas
            and wall identifiers.
        """
        return [
            {"dx": 0, "dy": -1, "wall": "N", "opp": "S"},
            {"dx": 1, "dy": 0, "wall": "E", "opp": "W"},
            {"dx": 0, "dy": 1, "wall": "S", "opp": "N"},
            {"dx": -1, "dy": 0, "wall": "W", "opp": "E"},
        ]

    def _is_inside_grid(self, x: int, y: int) -> bool:
        """
        Checks if a given coordinate is strictly within the maze boundaries.

        Args:
            x (int): The X coordinate.
            y (int): The Y coordinate.

        Returns:
            bool: True if inside the grid, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _get_generation_neighbors(
        self,
        x: int,
        y: int,
        visited: list[list[bool]],
    ) -> list[dict[str, int | str]]:
        """
        Retrieves unvisited neighboring cells for the DFS generation phase.

        Args:
            x (int): The current X coordinate.
            y (int): The current Y coordinate.
            visited (list[list[bool]]): The grid tracking visited cells.

        Returns:
            list[dict[str, int | str]]: A list of valid neighboring cells.
        """
        neighbors = []

        for direction in self._get_directions():
            nx = x + int(direction["dx"])
            ny = y + int(direction["dy"])

            if self._is_inside_grid(nx, ny) and not visited[ny][nx]:
                neighbors.append(
                    {
                        "x": nx,
                        "y": ny,
                        "wall": direction["wall"],
                        "opp": direction["opp"],
                    }
                )

        return neighbors

    def _get_accessible_neighbors(
        self,
        x: int,
        y: int,
        visited: list[list[bool]],
    ) -> list[dict[str, int]]:
        """
        Retrieves accessible neighboring cells (no blocking walls) for
        the BFS solving phase.

        Args:
            x (int): The current X coordinate.
            y (int): The current Y coordinate.
            visited (list[list[bool]]): The grid tracking visited cells.

        Returns:
            list[dict[str, int]]: A list of valid, unvisited,
            and accessible neighbors.
        """
        neighbors = []

        for direction in self._get_directions():
            nx = x + int(direction["dx"])
            ny = y + int(direction["dy"])
            wall = str(direction["wall"])

            if not self._is_inside_grid(nx, ny):
                continue

            if visited[ny][nx]:
                continue

            if self.grid[y][x][wall]:
                continue

            neighbors.append(
                {
                    "x": nx,
                    "y": ny,
                }
            )

        return neighbors

    def _remove_wall_between_cells(
        self,
        x: int,
        y: int,
        neighbor: dict[str, int | str],
    ) -> None:
        """
        Breaks down the mutual wall between the current cell
        and a chosen neighbor.

        Args:
            x (int): Current cell's X coordinate.
            y (int): Current cell's Y coordinate.
            neighbor (dict[str, int | str]): The target neighbor's data.
        """
        nx = int(neighbor["x"])
        ny = int(neighbor["y"])
        wall = str(neighbor["wall"])
        opposite_wall = str(neighbor["opp"])

        self.grid[y][x][wall] = False
        self.grid[ny][nx][opposite_wall] = False

    def _open_random_extra_wall(self, x: int, y: int) -> None:
        """
        Randomly breaks an additional East or South wall to create
        loops in an imperfect maze.

        Args:
            x (int): Current cell's X coordinate.
            y (int): Current cell's Y coordinate.
        """
        direction = random.choice(["E", "S"])

        if direction == "E":
            nx = x + 1
            ny = y
            opposite_wall = "W"
        else:
            nx = x
            ny = y + 1
            opposite_wall = "N"

        if self.is_pattern_cell(nx, ny):
            return

        self.grid[y][x][direction] = False
        self.grid[ny][nx][opposite_wall] = False

    def _reconstruct_path(
        self,
        parents: dict[tuple[int, int], tuple[int, int]],
    ) -> list[dict[str, int]]:
        """
        Reconstructs the shortest path from the exit back to the
        entry using the BFS tracking tree.

        Args:
            parents (dict): A dictionary linking a cell's coordinates
            to its parent's coordinates.

        Returns:
            list[dict[str, int]]: An ordered list of path coordinates
            from entry to exit.
        """
        path = []
        current = (self.exit_x, self.exit_y)
        start = (self.entry_x, self.entry_y)

        while current != start:
            path.append(
                {
                    "x": current[0],
                    "y": current[1],
                }
            )

            current = parents[current]

        path.append(
            {
                "x": self.entry_x,
                "y": self.entry_y,
            }
        )

        path.reverse()

        return path

    def _render_animation_frame(self) -> None:
        """
        Renders a single frame of the maze generation
        process in the terminal.
        Clears previous output and prints the current
        ASCII representation.
        """
        print("\033[H", end="")

        temp_grid = self.init_ascii_grid()
        self.apply_walls_to_ascii(temp_grid)

        frame = ""

        for line in temp_grid:
            line_str = "".join(line)
            line_str = line_str.replace("START ", "\033[92m██\033[0m")
            line_str = line_str.replace("END ", "\033[91m██\033[0m")
            frame += line_str + "\n"

        print(frame, end="", flush=True)
        sleep(0.01)

    def _clear_terminal(self) -> None:
        """
        Clears the terminal screen securely based on the operating system.
        """
        os.system("cls" if os.name == "nt" else "clear")

    def _cell_to_hex_value(self, cell: dict[str, bool]) -> int:
        """
        Converts a cell's wall configuration into its numerical equivalent
        (N=1, E=2, S=4, W=8) for hexadecimal export.

        Args:
            cell (dict[str, bool]): The dictionary representing
            the cell's walls.

        Returns:
            int: The calculated integer value.
        """
        value = 0

        if cell["N"]:
            value += 1
        if cell["E"]:
            value += 2
        if cell["S"]:
            value += 4
        if cell["W"]:
            value += 8

        return value

    def _path_to_directions(self, path: list[dict[str, int]]) -> str:
        """
        Converts a list of path coordinates into a string of
        directional moves (N, S, E, W).

        Args:
            path (list[dict[str, int]]): The ordered list of
            path coordinates.

        Returns:
            str: A string of successive directional instructions.
        """
        path_str = ""

        for index in range(len(path) - 1):
            current = path[index]
            next_cell = path[index + 1]

            if next_cell["y"] < current["y"]:
                path_str += "N"
            elif next_cell["y"] > current["y"]:
                path_str += "S"
            elif next_cell["x"] > current["x"]:
                path_str += "E"
            elif next_cell["x"] < current["x"]:
                path_str += "W"

        return path_str
