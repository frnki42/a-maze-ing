*This project has been created as part of the 42 curriculum by elfemboc, dpetutsc.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration
file, generates a random but reproducible maze, writes it to a file in a
hexadecimal wall format, and shows it in the terminal, where you can
regenerate it, show the shortest path and change the colours.

Every maze contains a "42" drawn with fully closed cells. Two modes are
available:

- **Perfect** (`PERFECT=True`): exactly one path between any two cells, no
  loops.
- **Playable board** (`PERFECT=False`, the default): a Pac-Man-style board
  with loops, so a chased player always has an alternative route, and
  almost no dead ends.

The generation logic is a standalone, pip-installable package, `mazegen`,
so it can be reused in later projects (see [Reusable code](#reusable-code-mazegen)).

## Instructions

### Requirements

- Python 3.10 or later
- `make`

### Installation

```
make install
```

This creates a virtual environment in `.venv/` and installs the pinned
development tools from `requirements.txt` (flake8, mypy, build). The
program itself only uses the Python standard library.

### Running

```
make run
```

or directly:

```
python3 a_maze_ing.py config.txt
```

`config.txt` is the default configuration file in this repository. Any
other file in the same format can be passed instead (see
[Configuration file](#configuration-file)).

### Make targets

| Target             | What it does                                                         |
|--------------------|----------------------------------------------------------------------|
| `make install`     | create `.venv/` and install the pinned tools                         |
| `make run`         | run the program with `config.txt`                                    |
| `make debug`       | run the program under `pdb`, Python's built-in debugger              |
| `make lint`        | `flake8 .` and `mypy .` with the flags required by the subject       |
| `make lint-strict` | `flake8 .` and `mypy . --strict`                                     |
| `make build`       | build the `mazegen` wheel and copy it to the repository root         |
| `make clean`       | remove caches and build artifacts (the root wheel is kept)           |

### Controls

While the maze is displayed, choose an action from the menu:

| Key | Action                                   |
|-----|------------------------------------------|
| `1` | generate a new maze (with a new seed)    |
| `2` | show / hide the shortest path            |
| `3` | switch to the next colour palette        |
| `4` | quit (`Ctrl+D` and `Ctrl+C` also quit)   |

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are
ignored, as are empty lines.

| Key           | Meaning                                   | Example               |
|---------------|-------------------------------------------|-----------------------|
| `WIDTH`       | maze width in cells                       | `WIDTH=20`            |
| `HEIGHT`      | maze height in cells                      | `HEIGHT=15`           |
| `ENTRY`       | entry cell as `x,y`                       | `ENTRY=0,0`           |
| `EXIT`        | exit cell as `x,y`                        | `EXIT=19,14`          |
| `OUTPUT_FILE` | file the maze is written to               | `OUTPUT_FILE=maze.txt`|
| `PERFECT`     | `True` for a perfect maze, else `False`   | `PERFECT=True`        |

All six keys are mandatory. Coordinates are `(x, y)` with `(0, 0)` in the
top-left corner, so `x` must be below `WIDTH` and `y` below `HEIGHT`. Entry
and exit must be different cells. Invalid files (missing or duplicate keys,
bad values, coordinates outside the maze) are rejected with a clear error
message instead of a crash.

Example:

```
# A-Maze-ing configuration file
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

TODO: check this section against the final config parser (accepted
whitespace, extra keys such as a seed, exact error messages).

## Output file

The maze is written to `OUTPUT_FILE` with one hexadecimal digit per cell,
one row per line. Each digit encodes the closed walls of its cell: bit 0 =
North, bit 1 = East, bit 2 = South, bit 3 = West (a set bit means the wall
is closed). After an empty line follow the entry coordinates, the exit
coordinates and the shortest path from entry to exit as a string of `N`,
`E`, `S`, `W`.

TODO: confirm against the final output writer.

## Maze generation algorithm

The maze is built in two steps.

**1. Recursive backtracker (randomized depth-first search).** Every cell
starts with all four walls closed. Starting at the entry, the algorithm
repeatedly moves to a random unvisited neighbour and opens the wall between
the two cells. When a cell has no unvisited neighbours left, it backtracks
to the previous cell. It is implemented with an explicit stack instead of
recursion, so large mazes cannot hit Python's recursion limit. The cells of
the "42" are marked as visited before the search starts, so the search
never enters them and they stay fully closed. The result is a perfect maze:
every cell is reachable and there is exactly one path between any two
cells. With `PERFECT=True` generation stops here.

**2. Braiding (only with `PERFECT=False`).** Every dead end (a cell with a
single opening) gets one extra wall opened, tried in random order. A wall is
skipped if it leads outside the maze, into the "42", or would create an
open area of 3x3 cells. Each opened wall adds a loop, which gives the
playable board its alternative routes.

Both steps use one `random.Random` instance created from the seed, so the
same seed and parameters always produce the same maze.

### Why this algorithm

- **Simple and verifiable.** The algorithm fits in a few lines, and its
  guarantees (full connectivity, exactly one path) follow directly from how
  it works.
- **Good-looking mazes.** It produces long, winding corridors with few short
  branches, which makes mazes harder to solve by eye than, for example,
  Prim's or Kruskal's algorithm.
- **Easy to constrain.** Keeping the "42" closed only requires marking its
  cells as visited up front.
- **One core for both modes.** The perfect maze is the starting point for
  the playable board, so both modes share the same tested code; braiding is
  a separate post-processing step.

## Reusable code: mazegen

The `mazegen` package (`mazegen/` in this repository) contains the maze
generation: the `MazeGenerator` class and the `Grid` it produces. It does
not print or write files, so it can be imported into any program. The
configuration parsing, terminal display and output file are part of the
A-Maze-ing program, not of the package.

The package is built as a wheel, `mazegen-1.0.0-py3-none-any.whl`, which
is kept at the repository root. To rebuild it from source:

```
make build
```

### Installation

Requires Python 3.10 or later. No third-party dependencies.

```
pip install mazegen-1.0.0-py3-none-any.whl
```

### Quick start

```python
from mazegen import MazeGenerator

gen = MazeGenerator(20, 15, entry=(0, 0), exit_cell=(19, 14), seed=42)
grid = gen.generate()

print(grid.width, grid.height)  # 20 15
print(gen.seed)                 # 42
```

### Parameters

| Parameter   | Type              | Default  | Meaning                                              |
|-------------|-------------------|----------|------------------------------------------------------|
| `width`     | `int`             | required | number of columns                                    |
| `height`    | `int`             | required | number of rows                                       |
| `entry`     | `tuple[int, int]` | required | entry cell `(x, y)`                                  |
| `exit_cell` | `tuple[int, int]` | required | exit cell `(x, y)`                                   |
| `perfect`   | `bool`            | `False`  | `True`: exactly one path between any two cells (no loops). `False`: a board with loops and few dead-ends |
| `seed`      | `int` or `None`   | `None`   | same seed and parameters give the same maze; `None` picks a random seed once |

### Accessing the maze

`generate()` returns the maze as a `Grid` (also available as `gen.grid`
afterwards):

| Member                       | Returns                | Meaning                                  |
|------------------------------|------------------------|------------------------------------------|
| `grid.width`, `grid.height`  | `int`                  | size in cells                            |
| `grid.in_bounds(x, y)`       | `bool`                 | whether `(x, y)` lies inside the grid    |
| `grid.walls(x, y)`           | `int`                  | the closed walls of a cell, as a bitmask |
| `grid.open_directions(x, y)` | `list[Direction]`      | the directions you can move from a cell  |
| `gen.pattern_cells`          | `set[tuple[int, int]]` | the fully closed cells drawing "42"; empty if the maze is too small for it |

`Direction` (`from mazegen.grid import Direction`) has the members `N`, `E`,
`S`, `W`, each with `.delta` (the `(dx, dy)` step) and `.opposite`. In the
bitmask from `grid.walls(x, y)`, a wall is closed when its bit is set
(`N` = 1, `E` = 2, `S` = 4, `W` = 8).

### Shortest path

TODO: document once shortest_path() is on main.

The full package documentation is in [MAZEGEN.md](MAZEGEN.md).

## Team and project management

### Roles

| Member   | Responsibilities                                                                 |
|----------|----------------------------------------------------------------------------------|
| elfemboc | repository setup, grid model, maze generator, terminal display, packaging, Makefile |
| dpetutsc | configuration parsing, pathfinding (shortest path), output file                  |

Both members reviewed each other's pull requests.

### Planning and how it evolved

- **Planned:** agree on a shared interface first (a `Grid` class wrapping one
  wall bitmask per cell), then work in parallel: generator and display on
  one side, config, pathfinding and output on the other, and wire
  everything together at the end.
- **Evolved:** TODO: fill in at the end of the project.

### What worked well and what could be improved

- **Worked well:** agreeing on the `Grid` interface early let both of us work
  independently; one branch per task with a reviewed pull request kept
  `main` working at all times.
- **Could be improved:** TODO: fill in at the end of the project.

### Tools

- Git and GitHub (feature branches, pull requests with reviews, merge commits)
- `make`, `venv` and `pip` for a reproducible development environment
- flake8 and mypy (including `--strict`) for style and type checking
- `build` and setuptools for packaging `mazegen` as a wheel
- `unittest` for tests of the config parser
- `maze_analyzer.py` (provided with the subject) to check the output files
- Neovim as editor
- Claude (AI assistant), see [AI usage](#ai-usage)

## Known limitations

- In playable-board mode, the "42" always leaves exactly 2 dead ends: two
  cells inside the notches of the "2" are enclosed by the pattern on three
  sides, so they cannot get a second opening without touching the "42".
- If the maze is too small for the "42" (smaller than 9x7 cells), it is
  generated without the pattern and an error message is printed.

## Resources

### References

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm):
  overview of the classic algorithms, including the randomized depth-first
  search used here
- [Maze Generation: Recursive Backtracking (Jamis Buck)](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking):
  step-by-step explanation of the recursive backtracker
- [Think Labyrinth: Maze Algorithms (Walter D. Pullen)](https://www.astrolog.org/labyrnth/algrithm.htm):
  maze terminology, including perfect and braid mazes
- [Introduction to the A* Algorithm (Red Blob Games)](https://www.redblobgames.com/pathfinding/a-star/introduction.html):
  breadth-first search, Dijkstra and A* for pathfinding
- [Python Packaging User Guide](https://packaging.python.org/): `pyproject.toml`
  and building wheels
- [PEP 8](https://peps.python.org/pep-0008/) and
  [PEP 257](https://peps.python.org/pep-0257/): code style and docstring
  conventions; docstrings follow the
  [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [mypy documentation](https://mypy.readthedocs.io/) and
  [flake8 documentation](https://flake8.pycqa.org/)

### AI usage

We used Claude (Anthropic) as a tutor and reviewer, not as a code
generator for the core logic. Everything AI-generated was checked by
running it, linting it and comparing it with the code.

- **Learning and guidance:** explanations of Python concepts, packaging
  (`pyproject.toml`, wheels), Makefile rules and Git workflow, mostly in the
  form of exercises that we solved ourselves.
- **Code review:** reviews of our code before pull requests, including a
  review of the config parser and pathfinding; the findings were tested and
  passed on to the author.
- **Documentation:** first drafts of `MAZEGEN.md`, the docstrings and this
  README, checked against the code (every documented behaviour was tested)
  and edited by us.

TODO: complete at the end of the project.

## License

Released under the MIT License, see [LICENSE.md](LICENSE.md). This also
covers the `mazegen` package, so it may be reused and redistributed by
later projects.
