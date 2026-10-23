"""Grid of maze cells with one bitmask of closed walls per cell.

Each cell stores its closed walls as an ``int``: bit ``Direction.N`` (1),
``Direction.E`` (2), ``Direction.S`` (4) and ``Direction.W`` (8) is set
when that wall is closed. Walls are always changed on both sides at once,
so neighbouring cells never disagree about the wall between them.
"""

from enum import IntFlag


class Direction(IntFlag):
    """A cardinal direction, usable as a wall bit in a cell bitmask.

    The values match the wall bits of the output file format: ``N`` = 1,
    ``E`` = 2, ``S`` = 4, ``W`` = 8.
    """

    N = 1
    E = 2
    S = 4
    W = 8

    @property
    def opposite(self) -> "Direction":
        """Direction: The direction pointing the other way (N <-> S)."""
        return _OPPOSITE[self]

    @property
    def delta(self) -> tuple[int, int]:
        """tuple[int, int]: The ``(dx, dy)`` step one cell in this direction.

        ``y`` grows downwards, so ``N`` is ``(0, -1)``.
        """
        return _DELTA[self]


_OPPOSITE: dict[Direction, Direction] = {
    Direction.N: Direction.S,
    Direction.E: Direction.W,
    Direction.S: Direction.N,
    Direction.W: Direction.E,
}


_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.N: (0, -1),
    Direction.E: (1, 0),
    Direction.S: (0, 1),
    Direction.W: (-1, 0),
}


DIRECTIONS: tuple[Direction, ...] = (
    Direction.N,
    Direction.E,
    Direction.S,
    Direction.W,
)


CLOSED_CELL: int = int(
    Direction.N | Direction.E | Direction.S | Direction.W
)


class Grid:
    """A rectangular grid of cells, each starting with all four walls closed.

    Coordinates are ``(x, y)``: ``x`` is the column, ``y`` is the row, and
    ``(0, 0)`` is the top-left cell.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a grid where every wall of every cell is closed.

        Args:
            width: Number of columns.
            height: Number of rows.
        """
        self._width = width
        self._height = height
        self._cells: list[list[int]] = [
            [CLOSED_CELL] * self._width for _ in range(self._height)
        ]

    @property
    def width(self) -> int:
        """int: Number of columns."""
        return self._width

    @property
    def height(self) -> int:
        """int: Number of rows."""
        return self._height

    def in_bounds(self, x: int, y: int) -> bool:
        """Check whether a cell lies inside the grid.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            True if ``(x, y)`` is inside the grid, False otherwise.
        """
        return 0 <= x < self._width and 0 <= y < self._height

    def walls(self, x: int, y: int) -> int:
        """Return the closed walls of a cell as a bitmask.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            The bitmask of closed walls; a ``Direction`` bit is set when
            that wall is closed.

        Raises:
            IndexError: If ``(x, y)`` is outside the grid.
        """
        if not self.in_bounds(x, y):
            raise IndexError(
                f"cell ({x}, {y}) is outside the "
                f"{self._width}x{self._height} grid"
            )
        return self._cells[y][x]

    def carve_wall(self, x: int, y: int, direction: Direction) -> None:
        """Open the wall between a cell and its neighbour.

        The wall is removed on both sides, so both cells stay consistent.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell whose wall is opened.

        Raises:
            IndexError: If the cell or its neighbour is outside the grid.
        """
        dx, dy = direction.delta
        nx, ny = x + dx, y + dy
        cell = self.walls(x, y)
        neighbour = self.walls(nx, ny)
        self._cells[y][x] = int(cell & ~direction)
        self._cells[ny][nx] = int(neighbour & ~direction.opposite)

    def close_wall(self, x: int, y: int, direction: Direction) -> None:
        """Close the wall between a cell and its neighbour.

        The wall is added on both sides, so both cells stay consistent.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell whose wall is closed.

        Raises:
            IndexError: If the cell or its neighbour is outside the grid.
        """
        dx, dy = direction.delta
        nx, ny = x + dx, y + dy
        cell = self.walls(x, y)
        neighbour = self.walls(nx, ny)
        self._cells[y][x] = int(cell | direction)
        self._cells[ny][nx] = int(neighbour | direction.opposite)

    def open_directions(self, x: int, y: int) -> list[Direction]:
        """Return the directions you can move from a cell.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            The directions whose wall is open, in the order N, E, S, W.

        Raises:
            IndexError: If ``(x, y)`` is outside the grid.
        """
        cell = self.walls(x, y)
        return [d for d in DIRECTIONS if not cell & d]
