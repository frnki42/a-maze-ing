import sys

from config import Config
from display import run


USAGE = "usage: python3 a_maze_ing.py <config_file>"
EXIT_ERROR = 1
EXIT_USAGE = 2


def main() -> int:
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    try:
        config = Config(sys.argv[1])
    except ValueError as e:
        print(f"Error: invalid config: {e}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as e:
        print(f"Error: cannot read config: {e}", file=sys.stderr)
        return EXIT_ERROR
    try:
        run(config)
    except ValueError as e:
        print(f"Error: invalid maze parameters: {e}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as e:
        print(f"Error: cannot write the output file: {e}", file=sys.stderr)
        return EXIT_ERROR
    return 0


if __name__ == "__main__":
    sys.exit(main())
