"""Seeded maze generation with a recursive backtracker.

``MazeGenerator`` carves a perfect maze (exactly one path between any two
cells) with an iterative depth-first search, keeps the cells of a "42"
pattern fully closed, and optionally braids the result: it removes dead
ends to add loops without creating open areas wider than 2 cells.
"""

import random

from .grid import DIRECTIONS, Direction, Grid


SEED_LIMIT = 2**32
PATTERN_42 = (
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
)


def _unvisited_directions(
    grid: Grid,
    visited: set[tuple[int, int]],
    x: int,
    y: int,
) -> list[Direction]:
    """List the directions that lead to an unvisited cell inside the grid.

    Args:
        grid: The grid being carved.
        visited: Cells already reached by the search.
        x: Column of the current cell.
        y: Row of the current cell.

    Returns:
        The directions, in the order N, E, S, W, whose neighbour is inside
        the grid and not yet visited.
    """
    unvisited_directions: list[Direction] = []
    for direction in DIRECTIONS:
        dx, dy = direction.delta
        nx, ny = x + dx, y + dy
        if grid.in_bounds(nx, ny) and (nx, ny) not in visited:
            unvisited_directions.append(direction)
    return unvisited_directions


def _check_cell(
    name: str,
    cell: tuple[int, int],
    width: int,
    height: int,
) -> None:
    """Check that a cell lies inside a maze of the given size.

    Args:
        name: Name of the cell for the error message, e.g. ``"entry"``.
        cell: The cell as ``(x, y)``.
        width: Number of columns of the maze.
        height: Number of rows of the maze.

    Raises:
        ValueError: If the cell is outside the maze.
    """
    x, y = cell
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"{name} {cell} is outside the {width}x{height} maze")


def _pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Compute the cells of the "42" pattern, centred in the maze.

    The pattern needs a margin of one cell on every side, so the maze must
    be at least 2 cells wider and taller than ``PATTERN_42``.

    Args:
        width: Number of columns of the maze.
        height: Number of rows of the maze.

    Returns:
        The ``(x, y)`` cells marked ``#`` in ``PATTERN_42``, or an empty set
        if the maze is too small for the pattern.
    """
    pattern_width = len(PATTERN_42[0])
    pattern_height = len(PATTERN_42)
    if width < pattern_width + 2 or height < pattern_height + 2:
        return set()
    origin_x = width // 2 - pattern_width // 2
    origin_y = height // 2 - pattern_height // 2
    cells: set[tuple[int, int]] = set()
    for row in range(pattern_height):
        for col in range(pattern_width):
            if PATTERN_42[row][col] == "#":
                cells.add((origin_x + col, origin_y + row))
    return cells


def _dead_ends(grid: Grid) -> list[tuple[int, int]]:
    """Find all cells with exactly one open wall.

    Args:
        grid: The grid to scan.

    Returns:
        The dead-end cells as ``(x, y)``, row by row from the top.
    """
    dead_ends: list[tuple[int, int]] = []
    for y in range(grid.height):
        for x in range(grid.width):
            if len(grid.open_directions(x, y)) == 1:
                dead_ends.append((x, y))
    return dead_ends


def _is_open_block(grid: Grid, left: int, top: int) -> bool:
    """Check whether a 3x3 block of cells has no walls inside it.

    Args:
        grid: The grid to check.
        left: Column of the block's top-left cell.
        top: Row of the block's top-left cell.

    Returns:
        True if all walls between the 9 cells are open, False otherwise.
    """
    for y in range(top, top + 3):
        for x in range(left, left + 3):
            open_dirs = grid.open_directions(x, y)
            if x < left + 2 and Direction.E not in open_dirs:
                return False
            if y < top + 2 and Direction.S not in open_dirs:
                return False
    return True


def _has_open_area(grid: Grid, x: int, y: int) -> bool:
    """Check whether any fully open 3x3 block contains a given cell.

    Args:
        grid: The grid to check.
        x: Column of the cell.
        y: Row of the cell.

    Returns:
        True if one of the 3x3 blocks inside the grid that contain
        ``(x, y)`` has no walls inside it, False otherwise.
    """
    for top in range(y - 2, y + 1):
        for left in range(x - 2, x + 1):
            if not grid.in_bounds(left, top):
                continue
            if not grid.in_bounds(left + 2, top + 2):
                continue
            if _is_open_block(grid, left, top):
                return True
    return False


def _braid(
    grid: Grid,
    pattern: set[tuple[int, int]],
    rng: random.Random,
) -> None:
    """Remove dead ends by opening one extra wall each, adding loops.

    For every dead end, the closed walls are tried in random order. The
    first one that does not lead outside the grid, into the "42" pattern,
    or to a 3x3 open area stays open. A dead end with no such wall is
    left as it is.

    Args:
        grid: The grid to modify in place.
        pattern: Cells of the "42" pattern, which must stay closed.
        rng: Random number generator, so the result follows the seed.
    """
    for x, y in _dead_ends(grid):
        if len(grid.open_directions(x, y)) != 1:
            continue
        candidates: list[Direction] = []
        for direction in DIRECTIONS:
            dx, dy = direction.delta
            nx, ny = x + dx, y + dy
            if not grid.in_bounds(nx, ny):
                continue
            if (nx, ny) in pattern:
                continue
            if direction in grid.open_directions(x, y):
                continue
            candidates.append(direction)
        rng.shuffle(candidates)
        for direction in candidates:
            grid.carve_wall(x, y, direction)
            if _has_open_area(grid, x, y):
                grid.close_wall(x, y, direction)
            else:
                break


class MazeGenerator:
    """Generates reproducible mazes from a size, an entry, an exit and a seed.

    Example:
        >>> gen = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
        >>> grid = gen.generate()
        >>> grid.width, grid.height
        (20, 15)
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_cell: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Validate the parameters and prepare the generator.

        Args:
            width: Number of columns, at least 1.
            height: Number of rows, at least 1.
            entry: Entry cell as ``(x, y)``.
            exit_cell: Exit cell as ``(x, y)``.
            perfect: If True, the maze has exactly one path between any two
                cells. If False, dead ends are removed where possible, which
                adds loops.
            seed: Seed for the random number generator. If None, a random
                seed is picked once and kept, see ``seed``.

        Raises:
            ValueError: If the size is smaller than 1x1, entry or exit lie
                outside the maze or inside the "42" pattern, or entry and
                exit are the same cell.
        """
        if width < 1 or height < 1:
            raise ValueError(f"invalid maze size {width}x{height}")
        _check_cell("entry", entry, width, height)
        _check_cell("exit", exit_cell, width, height)
        if entry == exit_cell:
            raise ValueError("entry and exit must be different")
        pattern = _pattern_cells(width, height)
        if entry in pattern or exit_cell in pattern:
            raise ValueError("entry and exit must be outside the 42 pattern")
        if seed is None:
            seed = random.randrange(SEED_LIMIT)
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_cell
        self._perfect = perfect
        self._seed = seed
        self._pattern = pattern
        self._grid: Grid | None = None

    @property
    def seed(self) -> int:
        """int: The seed used for generation.

        The same seed and parameters always give the same maze.
        """
        return self._seed

    @property
    def pattern_cells(self) -> set[tuple[int, int]]:
        """set[tuple[int, int]]: A copy of the fully closed "42" cells.

        Empty if the maze is too small for the pattern.
        """
        return set(self._pattern)

    @property
    def grid(self) -> Grid:
        """Grid: The maze built by the last call to ``generate()``.

        Raises:
            RuntimeError: If ``generate()`` has not been called yet.
        """
        if self._grid is None:
            raise RuntimeError("grid not set - use MazeGenerator.generate()")
        return self._grid

    def generate(self) -> Grid:
        """Build the maze and store it in ``grid``.

        The random number generator is recreated from ``seed`` on every
        call, so calling this again returns the same maze.

        Returns:
            The generated maze.
        """
        rng = random.Random(self._seed)
        grid = Grid(self._width, self._height)
        start = self._entry
        visited: set[tuple[int, int]] = set(self._pattern)
        visited.add(start)
        stack: list[tuple[int, int]] = [start]
        while stack:
            x, y = stack[-1]
            candidates = _unvisited_directions(grid, visited, x, y)
            if candidates:
                direction = rng.choice(candidates)
                grid.carve_wall(x, y, direction)
                dx, dy = direction.delta
                neighbour = (x + dx, y + dy)
                visited.add(neighbour)
                stack.append(neighbour)
            else:
                stack.pop()
        if not self._perfect:
            _braid(grid, self._pattern, rng)
        self._grid = grid
        return grid
