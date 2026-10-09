import unittest
from unittest.mock import mock_open, patch

from config import Config


class TestConfig(unittest.TestCase):
    """TestConfig containst the unittests for the config class."""

    def test_invalid_config(self):
        # These test-cases were ai-generated
        invalid_configs = [
            # 1. Missing a mandatory key (missing PERFECT)
            (
                "WIDTH=20\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
            ),
            # 2. Duplicate mandatory key with conflicting values
            (
                "WIDTH=20\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
                "WIDTH=40\n"
            ),
            # 3. Missing delimiter / invalid line syntax
            (
                "WIDTH:20\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 4. Empty value for a mandatory key
            (
                "WIDTH=\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 5. Non-numeric value for WIDTH and HEIGHT
            (
                "WIDTH=twenty\n"
                "HEIGHT=fifteen\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 6. Negative / non-positive dimensions
            (
                "WIDTH=-5\n"
                "HEIGHT=0\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 7. Invalid coordinate format (missing comma / extra dimension)
            (
                "WIDTH=20\n"
                "HEIGHT=15\n"
                "ENTRY=0 0\n"
                "EXIT=19,14,0\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 8. Entry and Exit coordinates out of bounds (>= WIDTH, HEIGHT)
            (
                "WIDTH=20\n"
                "HEIGHT=15\n"
                "ENTRY=25,3\n"
                "EXIT=19,20\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 9. Non-boolean value for PERFECT
            (
                "WIDTH=20\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=maybe\n"
            ),
            # 10. Multiple KEY=VALUE pairs on a single line
            (
                "WIDTH=20 HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 11. Mid-line comments breaking the format parser
            (
                "WIDTH=20 # maze width\n"
                "HEIGHT=15\n"
                "ENTRY=0,0\n"
                "EXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
            ),
            # 12. Empty file / only comments
            ("# Maze configuration\n# Missing all mandatory keys\n"),
        ]

        for i, config in enumerate(invalid_configs):
            with self.subTest(case_index=i + 1):
                m = mock_open(read_data=config)
                with (
                    patch("builtins.open", m),
                    self.assertRaises((AttributeError, TypeError, ValueError)),
                ):
                    Config("dummy/path/config.txt")


if __name__ == "__main__":
    unittest.main()
