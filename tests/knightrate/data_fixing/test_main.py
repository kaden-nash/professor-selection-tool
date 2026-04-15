import os
from unittest.mock import patch
from knightrate.data_fixing.main import main
from knightrate.data_fixing.data_fixing_runner import DataFixingRunner


def test_main_with_missing_files(capsys):
    with patch("os.path.exists", return_value=False):
        main()

    captured = capsys.readouterr()
    assert "skipping course scrub" in captured.out
    assert "skipping RMP scrub" in captured.out
    assert "skipping Catalog scrub" in captured.out


def test_main_with_all_files(tmp_path, monkeypatch):
    """Verifies the pipeline creates all expected output files."""
    monkeypatch.chdir(tmp_path)

    (tmp_path / "course_scraping").mkdir()
    (tmp_path / "rmp_scraping").mkdir()
    (tmp_path / "prof_scraping").mkdir()
    (tmp_path / "data_fixing").mkdir()

    (tmp_path / "course_scraping" / "courses.json").write_text("[]")
    (tmp_path / "rmp_scraping" / "rmp_data.json").write_text("[]")
    (tmp_path / "prof_scraping" / "ucf_catalog_professors.json").write_text("[]")

    with patch("os.path.exists", return_value=True):
        main(root_dir=str(tmp_path))

    assert (tmp_path / "data_fixing" / "courses_cleaned.json").exists()
    assert (tmp_path / "data_fixing" / "rmp_data_cleaned.json").exists()
    assert (tmp_path / "data_fixing" / "ucf_catalog_professors_cleaned.json").exists()
    assert (tmp_path / "data_fixing" / "professor_data.json").exists()


def test_runner_run_delegates_correctly(tmp_path):
    """Verifies DataFixingRunner.run() calls all internal stages."""
    runner = DataFixingRunner(str(tmp_path))
    with patch.object(runner, "_run_course_scrubber", return_value=None) as mock_c, \
         patch.object(runner, "_run_rmp_scrubber", return_value=None) as mock_r, \
         patch.object(runner, "_run_catalog_scrubber", return_value=None) as mock_cat, \
         patch.object(runner, "_run_correlator") as mock_corr:
        runner.run()
        mock_c.assert_called_once()
        mock_r.assert_called_once()
        mock_cat.assert_called_once()
        mock_corr.assert_called_once()
