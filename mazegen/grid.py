from enum import IntFlag


class Direction(IntFlag):
    N = 1
    E = 2
    S = 4
    W = 8

    @property
    def opposite(self) -> "Direction":
        return _OPPOSITE[self]


_OPPOSITE: dict[Direction, Direction] = {
    Direction.N: Direction.S,
    Direction.E: Direction.W,
    Direction.S: Direction.N,
    Direction.W: Direction.E,
}
