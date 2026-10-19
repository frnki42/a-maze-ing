from heapq import heappop, heappush
from itertools import count
from typing import Literal, overload

from .config import Config
from .grid import DIRECTIONS, Direction, Grid


class _Cell:
    """Represents a node in the grid for the A* search algorithm.

    Attributes:
        cost: The path cost from the start position to this cell (g-score).
        estimated_cost: The heuristic estimated cost from this cell to the goal
            (h-score).
        parent: The (x, y) coordinates of the preceding cell in the path.
    """

    cost: int
    parent: tuple[int, int] | None
    estimated_cost: int

    def __init__(
        self,
        cost: int,
        estimated_cost: int,
        parent: tuple[int, int] | None = None,
    ) -> None:
        """Initializes a _Cell instance.

        Args:
            cost: The path cost from the start position to this cell.
            estimated_cost: The heuristic estimated cost from this cell to the
                goal.
            parent: The (x, y) coordinates of the preceding cell, or None if
                this is the starting cell. Defaults to None.
        """
        self.cost = cost
        self.estimated_cost = estimated_cost
        self.parent = parent

    def total_estimated_cost(self) -> int:
        """Calculates the total evaluation function value (f-score).

        Returns:
            The sum of the exact path cost and estimated heuristic cost
            (cost + estimated_cost).
        """
        return self.cost + self.estimated_cost


def _trace_path(
    cell_details: list[list[_Cell | None]],
    goal: tuple[int, int],
) -> list[Direction]:
    """Reconstructs the sequence of directional moves from start to goal.

    Backtracks through parent references in `cell_details` starting at the
    goal coordinates until reaching the start node (a cell without a parent).

    Args:
        cell_details: A 2D list indexed by `[x][y]` storing `_Cell` metadata.
        goal: The (x, y) coordinate pair of the destination cell.

    Returns:
        A list of Direction enums representing the forward path from start to
        goal.
    """
    path = []
    current = goal
    while True:
        parent = cell_details[current[0]][current[1]].parent
        delta = (current[0] - parent[0], current[1] - parent[1])
        for direction in DIRECTIONS:
            if direction.delta == delta:
                path.append(direction)
        current = parent
        if not cell_details[current[0]][current[1]].parent:
            return path[::-1]


def _astar(
    grid: Grid, entry: tuple[int, int], goal: tuple[int, int]
) -> list[Direction]:
    """Executes the A* pathfinding algorithm to find the shortest path.

    Uses the Manhattan distance heuristic on an orthogonal grid.

    Args:
        grid: The Grid instance containing maze geometry and open passages.
        entry: The (x, y) coordinates of the starting cell.
        goal: The (x, y) coordinates of the target cell.

    Returns:
        A list of Direction steps from entry to goal, or an empty list if no
        path exists.
    """
    counter = count()
    openlist = [(0, next(counter), (entry[0], entry[1]))]
    closedlist = [
        [False for _ in range(grid.height)] for _ in range(grid.width)
    ]
    cell_details = [
        [None for _ in range(grid.height)] for _ in range(grid.width)
    ]
    cell_details[entry[0]][entry[1]] = _Cell(0, 0)

    while openlist:
        item = heappop(openlist)
        x, y = item[2]
        if closedlist[x][y]:
            continue
        closedlist[x][y] = True
        possible_moves = grid.open_directions(x, y)
        for move in possible_moves:
            delta_x, delta_y = move.delta
            new_x, new_y = x + delta_x, y + delta_y
            if not closedlist[new_x][new_y]:
                if goal[0] == new_x and goal[1] == new_y:
                    cell_details[new_x][new_y] = _Cell(0, 0, (x, y))
                    return _trace_path(cell_details, goal)
                else:
                    cost = cell_details[x][y].cost + 1
                    estimated_cost = abs(new_x - goal[0]) + abs(
                        new_y - goal[1]
                    )

                    if (
                        not cell_details[new_x][new_y]
                        or cell_details[new_x][new_y].total_estimated_cost()
                        > cost + estimated_cost
                    ):
                        heappush(
                            openlist,
                            (
                                cost + estimated_cost,
                                next(counter),
                                (new_x, new_y),
                            ),
                        )
                        cell_details[new_x][new_y] = _Cell(
                            cost, estimated_cost, (x, y)
                        )
    return []


@overload
def find_path(
    grid: Grid, config: Config, all_paths: Literal[True]
) -> list[list[Direction]]: ...


@overload
def find_path(
    grid: Grid, config: Config, all_paths: Literal[False] = False
) -> list[Direction]: ...


def find_path(
    grid: Grid, config: Config, all_paths: bool = False
) -> list[Direction] | list[list[Direction]]:
    """Finds path(s) through a grid between configured entry and goal points.

    Args:
        grid: The Grid environment to navigate.
        config: Configuration containing entry/goal coordinates and maze
            properties (e.g., whether the maze is `perfect`).
        all_paths: If True, returns a list containing all viable paths. If
            False, returns a single path. Defaults to False.

    Returns:
        A list of Direction steps if `all_paths` is False, or a list of such
        paths if `all_paths` is True.
    """
    if all_paths:
        if config.perfect:
            return [_astar(grid, config.entry, config.goal)]
        else:
            pass
    else:
        return _astar(grid, config.entry, config.goal)
