import os
from .data_fixing_runner import DataFixingRunner


def main(root_dir: str | None = None) -> None:
    """Entry point for standalone data-fixing execution."""
    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DataFixingRunner(root_dir).run()


if __name__ == "__main__":
    main()
