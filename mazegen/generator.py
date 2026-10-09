import random

from .grid import DIRECTIONS, Direction, Grid


SEED_LIMIT = 2**32


def _unvisited_directions(
    grid: Grid,
    visited: set[tuple[int, int]],
    x: int,
    y: int,
) -> list[Direction]:
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
    x, y = cell
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"{name} {cell} is outside the {width}x{height} maze")


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        if width < 1 or height < 1:
            raise ValueError(f"invalid maze size {width}x{height}")
        _check_cell("entry", entry, width, height)
        _check_cell("exit", exit_, width, height)
        if entry == exit_:
            raise ValueError("entry and exit must be different")
        if seed is None:
            seed = random.randrange(SEED_LIMIT)
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_
        self._perfect = perfect
        self._seed = seed
        self._grid: Grid | None = None

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def grid(self) -> Grid:
        if self._grid is None:
            raise RuntimeError("grid not set - use MazeGenerator.generate()")
        return self._grid

    def generate(self) -> Grid:
        rng = random.Random(self._seed)
        grid = Grid(self._width, self._height)
        start = self._entry
        visited: set[tuple[int, int]] = {start}
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
        self._grid = grid
        return grid
