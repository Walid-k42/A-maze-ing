#!/usr/bin/env python3

from pydantic import BaseModel, Field, model_validator, field_validator
from enum import Enum
from typing import Any, Annotated


PositiveInt = Annotated[int, Field(ge=0, le=100)]


class MazeConfig(BaseModel):

    width: int = Field(ge=5, le=100)
    height: int = Field(ge=5, le=100)
    entry: tuple[PositiveInt, PositiveInt]
    exit: tuple[PositiveInt, PositiveInt]
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

        if self.entry[1] > self.height or self.entry[0] > self.width:
            raise ValueError(f"Entry coordinates {self.entry} can't be "
                             f"outside the maze ({self.height}x{self.width})")

        if self.exit[1] > self.height or self.exit[0] > self.width:
            raise ValueError(f"Exit coordinates {self.exit} can't be "
                             f"outside the maze ({self.height}x{self.width})")

        if self.exit == self.entry:
            raise ValueError(f"The entry {self.entry} and the exit "
                             f"{self.exit} can't be at the same location")

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
