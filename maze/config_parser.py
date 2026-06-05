
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    width: int   # number of pixels, no need for float
    height: int  # same as above
    entry: tuple[int, int]  # cells are dicrete, no need for float
    exit_: tuple[int, int]  # same as above
    output_file: str
    perfect: bool

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError("WIDTH must be positive")
        if self.height <= 0:
            raise ValueError("HEIGHT must be positive")
        if self.entry[0] < 0 or self.entry[1] < 0:
            raise ValueError("Entry point coordinates must pe positive")
        if self.exit_[0] < 0 or self.exit_[1] < 0:
            raise ValueError("Entry point coordinates must pe positive")
        if self.entry[0] > self.width or self.exit_[0] > self.width:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry[1] > self.height or self.exit_[1] > self.height:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry == self.exit_:
            raise ValueError("Entry and exit point cannot be the same")


def str_to_bool(s: str) -> bool:
    stripped = s.strip().lower()
    true_values: list[str] = ['true', 'yes', 'on', '1']
    false_values: list[str] = ['false', 'no', 'off', '0']
    if stripped in true_values:
        return True
    elif stripped in false_values:
        return False
    else:
        raise ValueError("worng value for PERFECT flage")


def load_config(path: str) -> Config:
    raw: dict[str, str] = {}
    try:
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
                if key in raw:
                    print(f"duplicate key {key}, skipping...")
                    continue
                raw[key.strip()] = value.strip()
    except (OSError, UnicodeDecodeError) as e:
        print(e)
        exit(1)
    mandatory_keys: list[str] = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT',
                                 'OUTPUT_FILE', 'PERFECT']
    missing_keys = set(mandatory_keys) - set(raw.keys())
    if missing_keys:
        raise KeyError(f"missing required keys: {missing_keys}")
    ent_coord = raw['ENTRY'].split(',')
    if len(ent_coord) != 2:
        raise TypeError("wrong format for  'ENTRY', must be ENTRY=x,y")
    ext_coord = raw['EXIT'].split(',')
    if len(ext_coord) != 2:
        raise TypeError("wrong format for  'EXIT', must be EXIT=x,y")
    x_ent, y_ent = raw['ENTRY'].split(',')
    if not x_ent or not y_ent:
        raise ValueError("Entry coordinates cannot be empty")
    x_ext, y_ext = raw['EXIT'].split(',')
    if not x_ext or not y_ext:
        raise ValueError("Exit coordinates cannot be empty")
    return Config(
        width=int(raw['WIDTH']),
        height=int(raw['HEIGHT']),
        entry=(int(x_ent), int(y_ent)),
        exit_=(int(x_ext), int(y_ext)),
        output_file=raw['OUTPUT_FILE'],  # it is str by default
        perfect=str_to_bool(raw['PERFECT'])
        )
