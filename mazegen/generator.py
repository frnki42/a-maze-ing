import random

from .grid import Grid


SEED_LIMIT = 2**32


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
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_
        self._perfect = perfect
        if seed is None:
            seed = random.randrange(SEED_LIMIT)
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
        grid = Grid(self._width, self._height)
        self._grid = grid
        return grid
