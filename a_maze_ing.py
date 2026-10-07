import sys


USAGE = "usage: python3 a_maze_ing.py <config_file>"
EXIT_USAGE = 2


def main() -> int:
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    print("sup")
    return 0


if __name__ == "__main__":
    sys.exit(main())
