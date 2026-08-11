"""config.parser module.

This module parses and saves the config data using Pydantic.
Since the config data could contain anything it is considered as
untrusted and for this we have decided to use Pydantic over
@dataclass despite the added dependency for the benefit of
extensive validation and less verbosity (aka to be more Pythonic).
"""
from pydantic import BaseModel, model_validator, ConfigDict, Field
from typing import Any
from config.base import ConfigBase


# Hardcoded '42' wall geometry (mirrors maze/grid.py __wall_42).
_42_WALL_WIDTH = 8
_42_WALL_HEIGHT = 6
_42_OFFSETS: frozenset[tuple[int, int]] = frozenset({
    # '4'
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
    # '2'
    (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2), (4, 2),
    (4, 3), (4, 4), (5, 4), (6, 4),
})


def _is_on_42_wall(x: int, y: int, width: int, height: int) -> bool:
    """Return whether cell (x, y) lies on the centered '42' wall pattern."""
    if width < _42_WALL_WIDTH or height <= _42_WALL_HEIGHT:
        return False
    origin_x = (width // 2) - ((_42_WALL_WIDTH - 1) // 2)
    origin_y = (height // 2) - ((_42_WALL_HEIGHT - 1) // 2)
    return (x - origin_x, y - origin_y) in _42_OFFSETS


class Config(ConfigBase, BaseModel):
    """Configuration model for the maze application.

    This class saves the parsed configuration using:
        - Pydantic for post validation (model_validator)
        - frozen for immutability
        - ....
        - Field has not been used because it does not provide custom error
    """

    model_config = ConfigDict(frozen=True, extra='forbid')

    width: int = Field(le=99) # number of pixels, no need for float
    height: int = Field(le=99) # same as above
    entry: tuple[int, int]  # cells are discrete, no need for float
    exit: tuple[int, int] = Field(description='exit')  # same as above
    output_file: str
    perfect: bool
    seed: int | None = None

    def model_post_init(self, _: Any) -> None:
        """Perform post per-field validation to ensure values are in bounds.

        Validates that width and height are positive, and that entry and
        exit coordinates are non-negative.

        Raises:
            ValueError: If any validated constraint is violated.
        """
        if self.width <= 0:
            raise ValueError("WIDTH must be positive")
        if self.height <= 0:
            raise ValueError("HEIGHT must be positive")
        if self.entry[0] < 0 or self.entry[1] < 0:
            raise ValueError("ENTRY point coordinates must be positive")
        if self.exit[0] < 0 or self.exit[1] < 0:
            raise ValueError("EXIT point coordinates must be positive")

    @model_validator(mode='after')
    def post_validate(self) -> Any:
        """Perform cross-field validation to ensure full model coherence.

        Validates that entry and exit points are within the grid dimensions
        and that entry and exit are not the same point.

        Returns:
            Any: The validated model instance.

        Raises:
            ValueError: If cross-field validation fails.
        """
        if self.entry[0] >= self.width or self.exit[0] >= self.width:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry[1] >= self.height or self.exit[1] >= self.height:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT point cannot be the same")
        if _is_on_42_wall(self.entry[0], self.entry[1], self.width, self.height):
            raise ValueError("ENTRY point cannot lie on the '42' wall")
        if _is_on_42_wall(self.exit[0], self.exit[1], self.width, self.height):
            raise ValueError("EXIT point cannot lie on the '42' wall")
        return self


def load_config(path: str) -> Config:
    """Load and parse the configuration from a config file.

    Reads the config file line by line, parses each KEY=value pair,
    validates mandatory keys are present, and returns a Config instance.

    Args:
        path (str): Path to the configuration file.

    Returns:
        Config: The parsed configuration object.

    Raises:
        KeyError: If required keys are missing from the config file.
        TypeError: If entry or exit coordinates have wrong format.
        ValueError: If coordinate values are empty or invalid.
        OSError: If the config file cannot be read.
        UnicodeDecodeError: If the config file is not valid text.
    """
    raw: dict[str, Any] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('=')
            if len(parts) != 2:
                raise ValueError("each line must be in the format: " +
                                 " KEY=value")
            key, value = parts
            if not key.strip():
                raise ValueError("Empty KEY in line: " + f"'{line}'")
            if not value.strip():
                raise ValueError("Empty value in line: " + f"'{line}'")
            if key.lower() in raw:
                print(f"duplicate key {key}, skipping...")
                continue
            raw[key.strip().lower()] = value.strip()
    mandatory_keys: list[str] = ['width', 'height', 'entry', 'exit',
                                 'output_file', 'perfect']
    missing_keys = set(mandatory_keys) - set(raw.keys())
    if missing_keys:
        raise KeyError(f"missing required keys: {missing_keys}")
    if len(raw['entry'].split(',')) != 2:
        raise TypeError("wrong format for  'ENTRY', must be ENTRY=x,y")
    if len(raw['exit'].split(',')) != 2:
        raise TypeError("wrong format for  'EXIT', must be EXIT=x,y")
    x_ent, y_ent = raw['entry'].split(',')
    if not x_ent or not y_ent:
        raise ValueError("Entry coordinates cannot be empty")
    raw['entry'] = (x_ent, y_ent)
    x_ext, y_ext = raw['exit'].split(',')
    if not x_ext or not y_ext:
        raise ValueError("Exit coordinates cannot be empty")
    raw['exit'] = (x_ext, y_ext)
    return Config(**raw)