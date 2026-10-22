from heapq import heappop, heappush
from itertools import count

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
    path: list[Direction] = []
    current = goal
    while True:
        cell = cell_details[current[0]][current[1]]
        if cell is None or cell.parent is None:
            return path[::-1]
        parent = cell.parent
        delta = (current[0] - parent[0], current[1] - parent[1])
        for direction in DIRECTIONS:
            if direction.delta == delta:
                path.append(direction)
        current = parent


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
    cell_details: list[list[_Cell | None]] = [
        [None for _ in range(grid.height)] for _ in range(grid.width)
    ]
    cell_details[entry[0]][entry[1]] = _Cell(0, 0)

    while openlist:
        item = heappop(openlist)
        x, y = item[2]
        if closedlist[x][y]:
            continue
        closedlist[x][y] = True
        current_cell = cell_details[x][y]
        if current_cell is None:
            continue

        possible_moves = grid.open_directions(x, y)
        for move in possible_moves:
            delta_x, delta_y = move.delta
            new_x, new_y = x + delta_x, y + delta_y
            if not closedlist[new_x][new_y]:
                if goal[0] == new_x and goal[1] == new_y:
                    cell_details[new_x][new_y] = _Cell(0, 0, (x, y))
                    return _trace_path(cell_details, goal)
                else:
                    cost = current_cell.cost + 1
                    estimated_cost = abs(new_x - goal[0]) + abs(
                        new_y - goal[1]
                    )
                    target_cell = cell_details[new_x][new_y]

                    if (
                        target_cell is None
                        or target_cell.total_estimated_cost()
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


def _dfs(
    entry: tuple[int, int],
    goal: tuple[int, int],
    grid: Grid,
    path: list[Direction],
    all_paths: list[list[Direction]],
    visited: set[tuple[int, int]],
) -> None:
    """Finds all simple paths from entry to goal using DFS backtracking.

    Args:
        entry: The current (x, y) coordinates in the grid.
        goal: The target (x, y) destination coordinates.
        grid: The Grid instance containing open passages.
        path: The running list of Direction steps taken on the current branch.
        all_paths: The accumulator list where completed paths are stored.
        visited: Set of coordinate pairs currently on the active search path
            to prevent revisiting cells and forming cycles.
    """
    if entry[0] == goal[0] and entry[1] == goal[1]:
        all_paths.append(path.copy())
        return
    else:
        visited.add(entry)
        x, y = entry
        possible_moves = grid.open_directions(x, y)
        for move in possible_moves:
            delta_x, delta_y = move.delta
            new_x, new_y = x + delta_x, y + delta_y
            if (new_x, new_y) not in visited:
                path.append(move)
                _dfs((new_x, new_y), goal, grid, path, all_paths, visited)
                path.pop()

        visited.remove(entry)


def find_shortest_path(
    grid: Grid, entry: tuple[int, int], goal: tuple[int, int]
) -> list[Direction]:
    """Finds the shortest path through a grid between entry and goal points.

    Args:
        grid: The Grid environment to navigate.
        entry: The (x, y) coordinates of the starting cell.
        goal: The (x, y) coordinates of the target cell.

    Returns:
        A list of Direction steps representing the shortest path from entry to
        goal, or an empty list if no path exists.
    """
    return _astar(grid, entry, goal)
