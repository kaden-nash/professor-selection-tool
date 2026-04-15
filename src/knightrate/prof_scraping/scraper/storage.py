import json
import os
from typing import List

OUTPUT_FILENAME = "ucf_catalog_professors.json"


class DataStorage:
    """Writes parsed professor entries to a JSON file."""

    def __init__(self, output_dir: str):
        """
        :param output_dir: Directory where the output JSON file will be written.
        """
        self._output_path = os.path.join(output_dir, OUTPUT_FILENAME)

    def save(self, entries: List[str]) -> None:
        """Persist entries to disk as ``{"professors": [...]}``.

        Overwrites any existing file at the output path.
        """
        payload = {"professors": entries}
        with open(self._output_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=4, ensure_ascii=False)

    @property
    def output_path(self) -> str:
        """Absolute path of the file that will be written."""
        return self._output_path
