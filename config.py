import sys


_MAX_SIZE = 100

_REQUIRED_KEYS: dict[str, str] = {
    "width": "WIDTH",
    "height": "HEIGHT",
    "entry": "ENTRY",
    "goal": "EXIT",
    "output_file": "OUTPUT_FILE",
}


def _parse_int(key: str, value: str) -> int:
    """Converts a config value to an integer.

    Args:
        key: The config key, used in the error message.
        value: The text after the "=" sign.

    Returns:
        The value as an integer.

    Raises:
        ValueError: If the value is not an integer.
    """
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"{key} must be an integer, got '{value}'") from e


def _parse_coords(key: str, value: str) -> tuple[int, int]:
    """Converts a config value like "3,4" to a pair of integers.

    Args:
        key: The config key, used in the error message.
        value: The text after the "=" sign.

    Returns:
        The value as an (x, y) tuple.

    Raises:
        ValueError: If the value is not exactly two integers.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key} must be two integers x,y, got '{value}'")
    return (_parse_int(key, parts[0]), _parse_int(key, parts[1]))


class Config:
    """Handles the configuration for maze generation.

    Attributes:
        width: The width of the maze.
        height: The height of the maze.
        entry: The (x, y) coordinates for the maze entry point.
        goal: The (x, y) coordinates for the maze exit point.
        output_file: The file path where the generated maze will be saved.
        perfect: Whether the generated maze should be a perfect maze.
            Optional in the config file; defaults to False.
    """

    width: int
    height: int
    entry: tuple[int, int]
    goal: tuple[int, int]
    output_file: str
    perfect: bool = False

    def __init__(self, file_name: str):
        """Initializes the Config instance with data from the provided file.

        Args:
            file_name: The path to the configuration file.

        Raises:
            ValueError: If a key is missing or a value is invalid.
            OSError: If the configuration file cannot be opened or read.
        """
        self._load_config(file_name)
        self._validate_config()

    def _load_config(self, file_name: str) -> None:
        """Loads configuration key-value pairs from a file into the instance.

        Args:
            file_name: The path to the configuration file to read.

        Raises:
            OSError: If the file cannot be opened or read.
            ValueError: If a line is not KEY=VALUE, a number or coordinate
                is invalid, or PERFECT is neither 'True' nor 'False'.
        """
        with open(file_name, "r") as config_file:
            line_no = 0
            while True:
                line = config_file.readline()
                if not line:
                    break
                line_no += 1
                stripped = line.strip()
                if stripped == "" or stripped.startswith("#"):
                    continue
                try:
                    key, value = line.split(sep="=")
                except ValueError as e:
                    raise ValueError(
                        f"{file_name}, line {line_no}: expected KEY=VALUE, "
                        f"got '{stripped}'"
                    ) from e
                key = key.strip(" \n\t")
                value = value.strip(" \n\t")
                match key:
                    case "WIDTH":
                        self.width = _parse_int(key, value)
                    case "HEIGHT":
                        self.height = _parse_int(key, value)
                    case "ENTRY":
                        self.entry = _parse_coords(key, value)
                    case "EXIT":
                        self.goal = _parse_coords(key, value)
                    case "OUTPUT_FILE":
                        self.output_file = value
                    case "PERFECT":
                        if value == "True":
                            self.perfect = True
                        elif value == "False":
                            self.perfect = False
                        else:
                            raise ValueError(
                                "PERFECT needs to be either True or False."
                            )
                    case _:
                        print(
                            f"WARN: Config field '{key}' is not supported.",
                            file=sys.stderr,
                        )

    def _validate_config(self) -> None:
        """Validates that all required fields exist and are valid.

        Raises:
            ValueError: If a required key is missing, if width or height is
                less than 2 or more than _MAX_SIZE, if entry or goal does
                not contain two coordinates, if entry or goal lies outside
                the maze, or if output_file is empty.
        """
        missing: list[str] = []
        for attribute, key in _REQUIRED_KEYS.items():
            if not hasattr(self, attribute):
                missing.append(key)
        if missing:
            raise ValueError("missing keys: " + ", ".join(missing))
        if self.width < 2:
            raise ValueError("WIDTH needs to be at least two.")
        if self.height < 2:
            raise ValueError("HEIGHT needs to be at least two.")
        if self.width > _MAX_SIZE:
            raise ValueError(f"WIDTH cannot be more than {_MAX_SIZE}.")
        if self.height > _MAX_SIZE:
            raise ValueError(f"HEIGHT cannot be more than {_MAX_SIZE}.")
        if len(self.entry) != 2:
            raise ValueError(
                "ENTRY needs to have exactly two coordinates (x, y)"
            )
        if len(self.goal) != 2:
            raise ValueError(
                "EXIT needs to have exactly two coordinates (x, y)"
            )
        if self.goal[0] >= self.width or self.goal[0] < 0:
            raise ValueError("EXIT cannot be outside the maze (width).")
        if self.goal[1] >= self.height or self.goal[1] < 0:
            raise ValueError("EXIT cannot be outside the maze (height).")
        if self.entry[0] >= self.width or self.entry[0] < 0:
            raise ValueError("ENTRY cannot be outside the maze (width).")
        if self.entry[1] >= self.height or self.entry[1] < 0:
            raise ValueError("ENTRY cannot be outside the maze (height).")
        if self.output_file == "":
            raise ValueError("OUTPUT_FILE cannot be empty.")
