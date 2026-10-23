import sys

from config import Config
from mazegen import MazeGenerator
from mazegen.grid import Direction
from mazegen.pathfinding import find_shortest_path
from output import write_maze


USAGE = "usage: python3 a_maze_ing.py <config_file>"
EXIT_ERROR = 1
EXIT_USAGE = 2


def _make_maze(
    config: Config,
    seed: int | None,
) -> tuple[MazeGenerator, list[Direction]]:
    gen = MazeGenerator(
        config.width,
        config.height,
        config.entry,
        config.goal,
        config.perfect,
        seed,
    )
    grid = gen.generate()
    path = find_shortest_path(grid, config.entry, config.goal)
    write_maze(grid, config.entry, config.goal, path, config.output_file)
    return gen, path


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
        _make_maze(config, config.seed)
    except ValueError as e:
        print(f"Error: invalid maze parameters: {e}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as e:
        print(f"Error: cannot write the output file: {e}", file=sys.stderr)
        return EXIT_ERROR
    return 0


if __name__ == "__main__":
    sys.exit(main())
