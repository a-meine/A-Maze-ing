from abc import ABC


class ConfigBase(ABC):
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
