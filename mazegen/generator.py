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


def _pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
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
    dead_ends: list[tuple[int, int]] = []
    for y in range(grid.height):
        for x in range(grid.width):
            if len(grid.open_directions(x, y)) == 1:
                dead_ends.append((x, y))
    return dead_ends


def _is_open_block(grid: Grid, left: int, top: int) -> bool:
    for y in range(top, top + 3):
        for x in range(left, left + 3):
            open_dirs = grid.open_directions(x, y)
            if x < left + 2 and Direction.E not in open_dirs:
                return False
            if y < top + 2 and Direction.S not in open_dirs:
                return False
    return True


def _has_open_area(grid: Grid, x: int, y: int) -> bool:
    for top in range(y - 2, y + 1):
        for left in range(x - 2, x + 1):
            if not grid.in_bounds(left, top):
                continue
            if not grid.in_bounds(left + 2, top + 2):
                continue
            if _is_open_block(grid, left, top):
                return True
    return False


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
        pattern = _pattern_cells(width, height)
        if entry in pattern or exit_ in pattern:
            raise ValueError("entry and exit must be outside the 42 pattern")
        if seed is None:
            seed = random.randrange(SEED_LIMIT)
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_
        self._perfect = perfect
        self._seed = seed
        self._pattern = pattern
        self._grid: Grid | None = None

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def pattern_cells(self) -> set[tuple[int, int]]:
        return set(self._pattern)

    @property
    def grid(self) -> Grid:
        if self._grid is None:
            raise RuntimeError("grid not set - use MazeGenerator.generate()")
        return self._grid

    def generate(self) -> Grid:
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
        self._grid = grid
        return grid
