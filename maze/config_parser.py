"""
This module parses and saves the config data in class.
Since the config dta xould contain anything it is considered as
untrusted and for this we have decided to use Pydantic over
@dataclass depsite the added dependency for the benefit of
exentsive validation and less verbosity (aka to be more Pythonic)
"""
from pydantic import BaseModel, model_validator, ConfigDict, Field
from typing import Any


class Config(BaseModel):
    """
    this class saves the parsed confgurate, usnig:
        - Pydantic for post validation (model_validator)
        - forzen for immutablilty
        - ....
        - Field has not been used because it does not provide custom error
        """
    model_config = ConfigDict(frozen=True, extra='forbid')

    width: int = Field(le=100)  # number of pixels, no need for float
    height: int  # same as above
    entry: tuple[int, int]  # cells are dicrete, no need for float
    exit_: tuple[int, int] = Field(alias='exit')  # same as above
    output_file: str
    perfect: bool

    def model_post_init(self, __context: Any) -> None:
        """
        This function performs post per field validation  requirments
        to assure values in boundries.
        """
        if self.width <= 0:
            raise ValueError("WIDTH must be positive")
        if self.height <= 0:
            raise ValueError("HEIGHT must be positive")
        if self.entry[0] < 0 or self.entry[1] < 0:
            raise ValueError("ENTRY point coordinates must pe positive")
        if self.exit_[0] < 0 or self.exit_[1] < 0:
            raise ValueError("EXIT point coordinates must pe positive")

    @model_validator(mode='after')
    def post_validate(self) -> Any:
        """
        This method performs cross-field validaiton, it runs automatically
        after model_post_init and verfies that full model is coherent.
        """
        if self.entry[0] >= self.width or self.exit_[0] >= self.width:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry[1] >= self.height or self.exit_[1] >= self.height:
            raise ValueError("entry and exit point coordinates must in " +
                             "widthxheight range")
        if self.entry == self.exit_:
            raise ValueError("ENTRY and EXIT point cannot be the same")
        return self


def load_config(path: str) -> Config:
    """
    This funciton loads the config from the config file and
    parses the argument in a dict it returns an instance of Config
    """
    raw: dict[str, Any] = {}
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
                if key.lower() in raw:
                    print(f"duplicate key {key}, skipping...")
                    continue
                raw[key.strip().lower()] = value.strip()
    except (OSError, UnicodeDecodeError) as e:
        print(e)
        exit(1)
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
