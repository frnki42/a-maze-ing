"""mazegen: seeded maze generation library.

Create a ``MazeGenerator`` and call ``generate()`` to get the maze as a
``Grid``. The library never prints or writes files.
"""

from .generator import MazeGenerator

__all__ = ["MazeGenerator"]
