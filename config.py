import sys


_REQUIRED_KEYS: dict[str, str] = {
    "width": "WIDTH",
    "height": "HEIGHT",
    "entry": "ENTRY",
    "goal": "EXIT",
    "output_file": "OUTPUT_FILE",
}


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
            ValueError: If a line cannot be unpacked, an integer conversion
                fails, or the PERFECT field is neither 'True' nor 'False'.
        """
        with open(file_name, "r") as config_file:
            while True:
                line = config_file.readline()
                if not line:
                    break
                if line.startswith("#") or line == "\n":
                    continue
                try:
                    key, value = line.split(sep="=")
                except ValueError:
                    raise ValueError(
                       "Invalid line in config.txt."
                       "For configuration use the <FIELD>=<VALUE> notation."
                       "Line-comments must start with #"
                       "Empty lines cannot contain any whitespace."
                    )
                key = key.strip(" \n\t")
                value = value.strip(" \n\t")
                match key:
                    case "WIDTH":
                        self.width = int(value)
                    case "HEIGHT":
                        self.height = int(value)
                    case "ENTRY":
                        x, y = value.split(",")
                        self.entry = (int(x), int(y))
                    case "EXIT":
                        x, y = value.split(",")
                        self.goal = (int(x), int(y))
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
                less than 2, if entry or goal does not contain two
                coordinates, or if entry or goal lies outside the maze.
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
