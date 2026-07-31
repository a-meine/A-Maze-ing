"""config.base module."""
from abc import ABC


class ConfigBase(ABC):
    """Base class for maze configuration.

    Defines the required attributes for maze configuration including
    dimensions, entry/exit points, and maze type.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool