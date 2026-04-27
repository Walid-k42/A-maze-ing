#!/usr/bin/env python3
from typing import List, Set, Tuple


class MazeTester:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.pattern_cells: Set[Tuple[int, int]] = set()
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

        grid = [["#" for _ in range(ascii_width)] for _ in range(ascii_height)]

        for y in range(self.height):
            for x in range(self.width):

                char_x = x * 2 + 1
                char_y = y * 2 + 1

                if (x, y) in self.pattern_cells:
                    grid[char_y][char_x] = "@"
                else:
                    grid[char_y][char_x] = " "

        return grid

