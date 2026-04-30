"""
Module dedicated to parsing and strict validation of maze parameters.
Uses Pydantic to ensure all configuration rules are respected.
"""

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ValidationInfo
)
from enum import Enum # NOQA
from typing import Any, Annotated


PositiveInt = Annotated[int, Field(ge=0, le=100)]


class MazeConfig(BaseModel):
    """
    Data model for the maze configuration.
    Manages dimensions, entry/exit points, and specific business rules.
    """
    width: int
    height: int
    entry: tuple[PositiveInt, PositiveInt]
    exit: tuple[PositiveInt, PositiveInt]
    output_file: str
    perfect: bool = Field(default=False)
    seed: int | None = Field(default=None, ge=0)

    @field_validator('width', 'height')
    @classmethod
    def validate_dimensions(cls, value: int, info: ValidationInfo) -> int:
        """
        Checks that the dimensions (width and height) are between 5 and 100.

        Args:
            value (int): The value of the dimension being tested.
            info (ValidationInfo): Information about the field being validated.

        Returns:
            int: The validated value.
        """
        if value < 5 or value > 100:
            raise ValueError(f"Maze {info.field_name} must be between 5"
                             f" and 100 (got {value})")
        return value

    @field_validator('output_file')
    @classmethod
    def validate_extension(cls, value: str) -> str:
        """
        Verifies that the output file ends with the '.txt' extension.

        Args:
            value (str): The name of the output file.

        Returns:
            str: The validated file name.
        """
        if not value.endswith('.txt'):
            raise ValueError("Output file must be a .txt file")
        return value

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_string_to_tuple(cls, value: Any) -> Any:
        """
        Converts string-formatted coordinates (e.g., '0,0') into a
        tuple of integers.

        Args:
            value (Any): The raw value read from the configuration file.

        Returns:
            Any: A tuple of two integers if the conversion succeeds,
              otherwise the raw value.
        """
        if isinstance(value, tuple):
            return value

        if isinstance(value, str):
            parts = value.split(",")

            if len(parts) == 2:
                return (int(parts[0].strip()), int(parts[1].strip()))

        return value

    @model_validator(mode="after")
    def validate_maze_configs(self) -> 'MazeConfig':
        """
        Performs cross-validations after field initialization.
        Verifies that entry and exit points are within bounds, distinct,
        and do not overlap the central '42' pattern.

        Returns:
            MazeConfig: The validated instance.
        """
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

            pattern_cells = []
            for x, y in relative_coords:
                pattern_cells.append((start_x + x, start_y + y))

            if self.entry in pattern_cells:
                raise ValueError(f"Entry {self.entry} overlaps with "
                                 "the '42' pattern.")
            if self.exit in pattern_cells:
                raise ValueError(f"Exit {self.exit} overlaps with the"
                                 " '42' pattern.")

        return self


def read_and_split(filename: str) -> dict[str, Any]:
    """
    Reads the configuration file and extracts key/value pairs.
    Ignores comments starting with '#' and empty lines.

    Args:
        filename (str): The path to the configuration file.

    Returns:
        dict[str, Any]: A dictionary containing lowercase keys and
        their associated string values.
    """
    configs: dict = {}

    try:
        with open(filename, "r") as datas:
            for line in datas:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if not line:
                    continue
                if '=' in line:
                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    configs[key] = value

    except FileNotFoundError:
        print(f"Error: {filename} not found")

    return configs
