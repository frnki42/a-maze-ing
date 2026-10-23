"""Entry point: read a config file, then generate, save and show mazes.

Usage: python3 a_maze_ing.py <config_file>

Every error a user can cause (a bad config, impossible maze parameters,
an output file that cannot be written, Ctrl+C) ends with one line on
stderr and an exit code instead of a traceback: 1 = error, 2 = wrong
usage, 130 = interrupted.
"""

import sys

from config import Config
from display import run


USAGE = "usage: python3 a_maze_ing.py <config_file>"
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130


def main() -> int:
    """Run the program with the config file named on the command line.

    Parses the config, then hands it to the interactive display, which
    generates, solves, writes and shows the mazes. Errors are caught
    here and reported as one line on stderr.

    Returns:
        The exit code: 0 on success, ``EXIT_USAGE`` for a wrong number of
        arguments, ``EXIT_ERROR`` for an invalid config, invalid maze
        parameters or an output file that cannot be written.
    """
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
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(EXIT_INTERRUPTED)
