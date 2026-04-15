import json
import os
import pytest
from knightrate.prof_scraping.scraper.models import ProfessorEntry
from knightrate.prof_scraping.scraper.storage import DataStorage, OUTPUT_FILENAME


class TestDataStorageSave:
    """Tests for DataStorage.save()."""

    def test_creates_file_with_correct_structure(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save(["Entry A", "Entry B"])

        output_file = tmp_path / OUTPUT_FILENAME
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert "professors" in data
        assert data["professors"] == ["Entry A", "Entry B"]

    def test_empty_list_produces_empty_professors_array(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save([])

        output_file = tmp_path / OUTPUT_FILENAME
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["professors"] == []

    def test_overwrites_existing_file(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save(["Old entry"])
        storage.save(["New entry"])

        output_file = tmp_path / OUTPUT_FILENAME
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["professors"] == ["New entry"]

    def test_output_is_valid_utf8_json(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save(["Müller, Hans, Professor"])

        output_file = tmp_path / OUTPUT_FILENAME
        raw = output_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert data["professors"][0] == "Müller, Hans, Professor"


class TestDataStorageOutputPath:
    """Tests for the output_path property."""

    def test_output_path_uses_provided_dir(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        expected = os.path.join(str(tmp_path), OUTPUT_FILENAME)
        assert storage.output_path == expected


class TestProfessorEntry:
    """Tests for the ProfessorEntry model."""

    def test_raw_field_is_stored(self):
        entry = ProfessorEntry(raw="Abbas, Hadi, Professor")
        assert entry.raw == "Abbas, Hadi, Professor"

    def test_empty_raw_is_accepted(self):
        entry = ProfessorEntry(raw="")
        assert entry.raw == ""
