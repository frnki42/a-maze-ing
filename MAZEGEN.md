# mazegen

Seeded maze generation library.

`mazegen` generates rectangular mazes on a grid of cells. Every maze can be
reproduced from its seed. The maze is returned as a `Grid` object you can
query; the library never prints or writes files, so it fits into any program.

## Installation

Requires Python 3.10 or later. No third-party dependencies.

```
pip install mazegen-1.0.0-py3-none-any.whl
```

To build the wheel yourself from the source repository:

```
pip install build
python -m build --wheel
```

The wheel is written to `dist/`.

## Quick start

```python
from mazegen import MazeGenerator

gen = MazeGenerator(20, 15, entry=(0, 0), exit_cell=(19, 14), seed=42)
grid = gen.generate()

print(grid.width, grid.height)  # 20 15
print(gen.seed)                 # 42
```

Coordinates are `(x, y)`: `x` is the column (`0` to `width - 1`), `y` is the
row (`0` to `height - 1`), and `(0, 0)` is the top-left cell.

## Parameters

| Parameter   | Type              | Default  | Meaning                                              |
|-------------|-------------------|----------|------------------------------------------------------|
| `width`     | `int`             | required | number of columns                                    |
| `height`    | `int`             | required | number of rows                                       |
| `entry`     | `tuple[int, int]` | required | entry cell `(x, y)`                                  |
| `exit_cell` | `tuple[int, int]` | required | exit cell `(x, y)`                                   |
| `perfect`   | `bool`            | `False`  | `True`: exactly one path between any two cells (no loops). `False`: a board with loops; dead ends are removed wherever the "42" and the border allow it |
| `seed`      | `int` or `None`   | `None`   | same seed and parameters give the same maze; `None` picks a random seed once |

The same seed always gives the same maze, so a maze can be shared by its seed:

```python
gen = MazeGenerator(20, 15, (0, 0), (19, 14))   # no seed given
print(gen.seed)                                 # the seed that was picked

again = MazeGenerator(20, 15, (0, 0), (19, 14), seed=gen.seed)
# again.generate() builds exactly the same maze as gen.generate()
```

Calling `generate()` twice on the same generator also returns the same maze.

## Accessing the maze

`generate()` returns the maze as a `Grid`. After that it is also available as
`gen.grid` (reading `gen.grid` before `generate()` raises `RuntimeError`).

| Member                       | Returns                | Meaning                                  |
|------------------------------|------------------------|------------------------------------------|
| `grid.width`, `grid.height`  | `int`                  | size in cells                            |
| `grid.in_bounds(x, y)`       | `bool`                 | whether `(x, y)` lies inside the grid    |
| `grid.walls(x, y)`           | `int`                  | the closed walls of a cell, as a bitmask |
| `grid.open_directions(x, y)` | `list[Direction]`      | the directions you can move from a cell  |
| `gen.pattern_cells`          | `set[tuple[int, int]]` | the fully closed cells drawing "42"; empty if the maze is too small for it |

`Direction` (`from mazegen.grid import Direction`) has the members `N`, `E`,
`S`, `W`. Each member has `.delta`, the `(dx, dy)` step in that direction, and
`.opposite`.

In the bitmask from `grid.walls(x, y)`, a wall is closed when its bit is set
(`N` = 1, `E` = 2, `S` = 4, `W` = 8):

```python
from mazegen.grid import Direction

if grid.walls(0, 0) & Direction.N:
    print("north wall of (0, 0) is closed")
```

Listing the neighbours you can reach from the entry:

```python
for d in grid.open_directions(0, 0):
    dx, dy = d.delta
    print(d.name, "->", (0 + dx, 0 + dy))
```

## Shortest path

`find_shortest_path` (in `mazegen.pathfinding`) returns a shortest route
between two cells as a list of `Direction` steps. It uses A* with the
Manhattan distance as heuristic, so the result is a shortest path in both
modes, also when the maze has loops.

```python
from mazegen import MazeGenerator
from mazegen.pathfinding import find_shortest_path

gen = MazeGenerator(20, 15, entry=(0, 0), exit_cell=(19, 14), seed=42)
grid = gen.generate()
path = find_shortest_path(grid, (0, 0), (19, 14))

letters = ""
for step in path:
    letters += step.name

print(len(path))  # 39
print(letters)    # SSSSSESWSSSSSSSESEEEEEEEEEEEENNESSEEEEE
```

| Parameter | Type              | Meaning                    |
|-----------|-------------------|----------------------------|
| `grid`    | `Grid`            | the maze from `generate()` |
| `entry`   | `tuple[int, int]` | start cell `(x, y)`        |
| `goal`    | `tuple[int, int]` | target cell `(x, y)`       |

It returns an empty list if `entry` and `goal` are the same cell or if
`goal` cannot be reached (for example a cell of the "42"). Following the
steps from `entry` with each `Direction.delta` leads to `goal`.
