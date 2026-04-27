from typing import List, Set, Tuple
import random


class MazeTester:
    def __init__(self, width: int, height: int, entry: Tuple[int, int], exit_coords: Tuple[int, int]) -> None:
        self.width = width
        self.height = height
        self.entry_coords = entry
        self.exit_coords = exit_coords
        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.pattern_cells: Set[Tuple[int, int]] = set()
        self.wall_char = "█" 
        self.pattern_char = "▓"
        self._setup_42_pattern()

    def _setup_42_pattern(self) -> None:
        p_width, p_height = 7, 5
        if self.width < p_width or self.height < p_height:
            print("Error: Maze size is too small to display the '42' pattern.")
            return

        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_height) // 2

        relative_coords = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2),
            (2, 3), (2, 4), (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        self.pattern_cells = {
            (start_x + dx, start_y + dy) for dx, dy in relative_coords
        }

    def _init_ascii_grid(self) -> List[List[str]]:
        ascii_width = 2 * self.width + 1
        ascii_height = 2 * self.height + 1
        grid = [[self.wall_char for _ in range(ascii_width)] for _ in range(ascii_height)]

        for y in range(self.height):
            for x in range(self.width):
                char_x = x * 2 + 1
                char_y = y * 2 + 1
                if (x, y) in self.pattern_cells:
                    grid[char_y][char_x] = self.pattern_char
                else:
                    grid[char_y][char_x] = " "
        return grid

    def _apply_walls_to_ascii(self, ascii_grid: List[List[str]]) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                val = self.grid[y][x]
                cx, cy = x * 2 + 1, y * 2 + 1
                if not (val & 1):
                    ascii_grid[cy - 1][cx] = " "
                if not (val & 2):
                    ascii_grid[cy][cx + 1] = " "
                if not (val & 4):
                    ascii_grid[cy + 1][cx] = " "
                if not (val & 8):
                    ascii_grid[cy][cx - 1] = " "

    def generate(self, seed: int = None) -> None:
        if seed is not None:
            random.seed(seed)
        stack = [self.entry_coords]
        visited = {self.entry_coords} | self.pattern_cells
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            directions = [(0, -1, 1, 4), (1, 0, 2, 8), (0, 1, 4, 1), (-1, 0, 8, 2)]
            for dx, dy, bit, opp in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, bit, opp))
            if neighbors:
                nx, ny, bit, opp = random.choice(neighbors)
                self.grid[cy][cx] -= bit
                self.grid[ny][nx] -= opp
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
