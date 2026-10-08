from enum import IntFlag


class Direction(IntFlag):
    N = 1
    E = 2
    S = 4
    W = 8

    @property
    def opposite(self) -> "Direction":
        return _OPPOSITE[self]

    @property
    def delta(self) -> tuple[int, int]:
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
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._cells: list[list[int]] = [
            [CLOSED_CELL] * self.width for _ in range(self.height)
        ]
