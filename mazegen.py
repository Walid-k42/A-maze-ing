from __future__ import annotations

import os
import random
from collections import deque
from time import sleep


class MazeTester:
    def __init__(
        self,
        width: int,
        height: int,
        entry: list[int],
        exit_p: list[int],
        is_perfect: bool = True,
    ) -> None:
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
        for cell in self.pattern_cells:
            if cell["x"] == check_x and cell["y"] == check_y:
                return True

        return False

    def init_ascii_grid(self) -> list[list[str]]:
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

                visited[chosen["y"]][chosen["x"]] = True
                stack.append(
                    {
                        "x": chosen["x"],
                        "y": chosen["y"],
                    }
                )
            else:
                stack.pop()

        if not self.is_perfect:
            self.make_imperfect(chance=0.2, animate=animate)

    def solve(self) -> list[dict[str, int]]:
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
        return [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _mark_pattern_cells_as_visited(
        self,
        visited: list[list[bool]],
    ) -> None:
        for cell in self.pattern_cells:
            visited[cell["y"]][cell["x"]] = True

    def _get_directions(self) -> list[dict[str, int | str]]:
        return [
            {"dx": 0, "dy": -1, "wall": "N", "opp": "S"},
            {"dx": 1, "dy": 0, "wall": "E", "opp": "W"},
            {"dx": 0, "dy": 1, "wall": "S", "opp": "N"},
            {"dx": -1, "dy": 0, "wall": "W", "opp": "E"},
        ]

    def _is_inside_grid(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _get_generation_neighbors(
        self,
        x: int,
        y: int,
        visited: list[list[bool]],
    ) -> list[dict[str, int | str]]:
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
        nx = int(neighbor["x"])
        ny = int(neighbor["y"])
        wall = str(neighbor["wall"])
        opposite_wall = str(neighbor["opp"])

        self.grid[y][x][wall] = False
        self.grid[ny][nx][opposite_wall] = False

    def _open_random_extra_wall(self, x: int, y: int) -> None:
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
        os.system("cls" if os.name == "nt" else "clear")

    def _cell_to_hex_value(self, cell: dict[str, bool]) -> int:
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