import random
from time import sleep
import os


class MazeTester:
    def __init__(self, width: int, height: int,
                 entry: list[int], exit_p: list[int]) -> None:
        self.width = width
        self.height = height
        self.entry_x = entry[0]
        self.entry_y = entry[1]
        self.exit_x = exit_p[0]
        self.exit_y = exit_p[1]
        self.wall_char = "██"
        self.pattern_char = "▓▓"
        self.grid = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append({"N": True, "E": True, "S": True, "W": True})
            self.grid.append(row)
        self.pattern_cells = []
        self.setup_42_pattern()

    def setup_42_pattern(self) -> None:
        p_width = 7
        p_height = 5
        if self.width < p_width or self.height < p_height:
            print("Error: Maze size is too small to display the '42' pattern.")
            return
        start_x = int((self.width - p_width) / 2)
        start_y = int((self.height - p_height) / 2)
        relative_coords = [
            {"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2},
            {"x": 1, "y": 2}, {"x": 2, "y": 0}, {"x": 2, "y": 1},
            {"x": 2, "y": 2}, {"x": 2, "y": 3}, {"x": 2, "y": 4},
            {"x": 4, "y": 0}, {"x": 5, "y": 0}, {"x": 6, "y": 0},
            {"x": 6, "y": 1}, {"x": 4, "y": 2}, {"x": 5, "y": 2},
            {"x": 6, "y": 2}, {"x": 4, "y": 3}, {"x": 4, "y": 4},
            {"x": 5, "y": 4}, {"x": 6, "y": 4}
        ]
        for coord in relative_coords:
            self.pattern_cells.append({
                "x": start_x + coord["x"],
                "y": start_y + coord["y"]
            })

    def is_pattern_cell(self, check_x: int, check_y: int) -> bool:
        for cell in self.pattern_cells:
            if cell["x"] == check_x and cell["y"] == check_y:
                return True
        return False

    def init_ascii_grid(self) -> list[list[str]]:
        ascii_width = 2 * self.width + 1
        ascii_height = 2 * self.height + 1
        grid = []
        for y in range(ascii_height):
            row = []
            for x in range(ascii_width):
                row.append(self.wall_char)
            grid.append(row)
        for y in range(self.height):
            for x in range(self.width):
                char_x = x * 2 + 1
                char_y = y * 2 + 1
                if x == self.entry_x and y == self.entry_y:
                    grid[char_y][char_x] = "S "
                elif x == self.exit_x and y == self.exit_y:
                    grid[char_y][char_x] = "E "
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

    def generate(self, seed: int | None = None, animate: bool = False) -> None:
        if seed is not None:
            random.seed(seed)
        stack = [{"x": self.entry_x, "y": self.entry_y}]
        visited = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(False)
            visited.append(row)
        for cell in self.pattern_cells:
            visited[cell["y"]][cell["x"]] = True

        visited[self.entry_y][self.entry_x] = True
        while len(stack) > 0:
            if animate:
                os.system('clear')
                temp_grid = self.init_ascii_grid()
                self.apply_walls_to_ascii(temp_grid)
                for row in temp_grid:
                    print("".join(row))
                sleep(0.002)
            current = stack[-1]
            cx = current["x"]
            cy = current["y"]
            neighbors = []
            directions = [
                {"dx": 0, "dy": -1, "wall": "N", "opp": "S"},
                {"dx": 1, "dy": 0, "wall": "E", "opp": "W"},
                {"dx": 0, "dy": 1, "wall": "S", "opp": "N"},
                {"dx": -1, "dy": 0, "wall": "W", "opp": "E"}
            ]
            for d in directions:
                nx = cx + d["dx"]
                ny = cy + d["dy"]
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx]:
                        neighbors.append({
                            "x": nx, "y": ny,
                            "wall": d["wall"], "opp": d["opp"]
                        })
            if len(neighbors) > 0:
                chosen = random.choice(neighbors)
                self.grid[cy][cx][chosen["wall"]] = False
                self.grid[chosen["y"]][chosen["x"]][chosen["opp"]] = False
                visited[chosen["y"]][chosen["x"]] = True
                stack.append({"x": chosen["x"], "y": chosen["y"]})
            else:
                stack.pop()

    def solve(self) -> list[dict[str, int]]:
        queue = [{"x": self.entry_x, "y": self.entry_y}]
        visited = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(False)
            visited.append(row)
        parents = {}
        visited[self.entry_y][self.entry_x] = True
        target_found = False
        while len(queue) > 0:
            current = queue.pop(0)
            cx = current["x"]
            cy = current["y"]
            if cx == self.exit_x and cy == self.exit_y:
                target_found = True
                break
            directions = [
                {"dx": 0, "dy": -1, "wall": "N"},
                {"dx": 1, "dy": 0, "wall": "E"},
                {"dx": 0, "dy": 1, "wall": "S"},
                {"dx": -1, "dy": 0, "wall": "W"}
            ]
            for d in directions:
                nx = cx + d["dx"]
                ny = cy + d["dy"]
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx] and not self.grid[cy][cx][d["wall"]]:
                        visited[ny][nx] = True
                        parents[(nx, ny)] = (cx, cy)
                        queue.append({"x": nx, "y": ny})
        path = []
        if target_found:
            curr = (self.exit_x, self.exit_y)
            while curr != (self.entry_x, self.entry_y):
                path.append({"x": curr[0], "y": curr[1]})
                curr = parents[curr]
            path.append({"x": self.entry_x, "y": self.entry_y})
        return path
