import sys


class Config:
    """Config handles the configuration for the maze-generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

    def __init__(self, file_name: str):
        """
        Instantiates the config class with the data in the
        config file provided.

        Throws:
            - ValueError
            - TypeError
            - OSError
            - AttributeError
        """
        self._load_config(file_name)
        self._validate_config()

    def _load_config(self, file_name: str) -> None:
        """Protected method for loading a file into self."""

        seen_keys = set()
        with open(file_name, "r") as config_file:
            while True:
                line = config_file.readline()
                if not line:
                    break
                if line.startswith("#") or line == "\n":
                    continue
                key, value = line.split(sep="=")
                key = key.strip(" \n\t")
                if key in seen_keys:
                    raise ValueError(f"Duplicate configuration key: {key}")
                seen_keys.add(key)
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
                        self.exit = (int(x), int(y))
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
                            f"WARN: Config field {key} is not supported.",
                            file=sys.stderr,
                        )

    def _validate_config(self) -> None:
        """Protected method for validating field values."""
        if not all(
            hasattr(self, attribute) for attribute in self.__annotations__
        ):
            raise AttributeError(
                "Missing values in the configuration file.",
                "Attributes required: ",
                [attr.upper() for attr in self.__annotations__],
            )
        if self.width < 2:
            raise ValueError("WIDTH needs to be at least two.")
        if self.height < 2:
            raise ValueError("HEIGHT needs to be at least two.")
        if len(self.entry) != 2:
            raise ValueError(
                "ENTRY needs to have exactly two coordinates (x, y)"
            )
        if len(self.exit) != 2:
            raise ValueError(
                "EXIT needs to have exactly two coordinates (x, y)"
            )
        if self.exit[0] > self.width:
            raise ValueError("EXIT cannot be outside the maze (width).")
        if self.exit[1] > self.height:
            raise ValueError("EXIT cannot be outside the maze (height).")
        if self.entry[0] > self.width:
            raise ValueError("ENTRY cannot be outside the maze (width).")
        if self.entry[1] > self.height:
            raise ValueError("ENTRY cannot be outside the maze (height).")
