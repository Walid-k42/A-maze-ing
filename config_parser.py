#!/usr/bin/env python3

from pydantic import BaseModel, Field, model_validator, field_validator
from enum import Enum # NOQA
from typing import Any, Annotated


PositiveInt = Annotated[int, Field(ge=0, le=100)]


class MazeConfig(BaseModel):

    width: int = Field(ge=5, le=100)
    height: int = Field(ge=5, le=100)
    entry: tuple[PositiveInt, PositiveInt]
    exit: tuple[PositiveInt, PositiveInt]
    output_file: str
    perfect: bool = Field(default=False)

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_string_to_tuple(cls, value: Any) -> Any:
        if isinstance(value, tuple):
            return value

        if isinstance(value, str):
            parts = value.split(",")

            if len(parts) == 2:
                return (int(parts[0].strip()), int(parts[1].strip()))

        return value

    @model_validator(mode="after")
    def validate_maze_configs(self) -> 'MazeConfig':

        if self.entry[1] >= self.height or self.entry[0] >= self.width:
            raise ValueError(f"Entry coordinates {self.entry} can't be "
                             f"outside the maze ({self.height}x{self.width})")

        if self.exit[1] >= self.height or self.exit[0] >= self.width:
            raise ValueError(f"Exit coordinates {self.exit} can't be "
                             f"outside the maze ({self.height}x{self.width})")

        if self.exit == self.entry:
            raise ValueError(f"The entry {self.entry} and the exit "
                             f"{self.exit} can't be at the same location")

        p_width = 7
        p_height = 5
        safe_width = 11
        safe_height = 9

        if self.width >= safe_width and self.height >= safe_height:
            start_x = int((self.width - p_width) / 2)
            start_y = int((self.height - p_height) / 2)

            relative_coords = [
                (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1),
                (2, 2), (2, 3), (2, 4), (4, 0), (5, 0), (6, 0),
                (6, 1), (4, 2), (5, 2), (6, 2), (4, 3), (4, 4),
                (5, 4), (6, 4)
            ]

            pattern_cells = [(start_x + x, start_y + y) for x, y in relative_coords]

            if self.entry in pattern_cells:
                raise ValueError(f"Entry {self.entry} overlaps with the '42' pattern.")
            if self.exit in pattern_cells:
                raise ValueError(f"Exit {self.exit} overlaps with the '42' pattern.")

        return self


def read_and_split(filename: str) -> dict[str, Any]:

    configs: dict = {}

    try:
        with open(filename, "r") as datas:
            for line in datas:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    configs[key] = value

    except FileNotFoundError:
        print(f"Error: {filename} not found")

    return configs
