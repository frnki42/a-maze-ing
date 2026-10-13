import sys
from mazegen.config import Config


USAGE = "usage: python3 a_maze_ing.py <config_file>"
EXIT_USAGE = 2


def main() -> int:
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    print("sup")
    try:
        Config(sys.argv[1])
    except (ValueError, TypeError, AttributeError) as ex:
        print("Error parsing config:", ex, file=sys.stderr)
        return 1
    except OSError as ex:
        print("Error reading conig:", ex, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
