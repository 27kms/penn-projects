"""Regression checks using synthetic files, without loading historical course data."""

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from check_archive import EXPECTED_SOURCE_COUNT, check_archive


class ArchiveChecksTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text("# Synthetic archive\n")
        self.notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{
                "cell_type": "code",
                "source": "STUDENT_ID = 'XXXXXXXX'\n",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
            }],
        }
        (self.root / "notebook.ipynb").write_text(json.dumps(self.notebook))
        paths = ["notebook.ipynb", "docs/original-readme.md"]
        paths.extend(f"asset-{i}.txt" for i in range(EXPECTED_SOURCE_COUNT - 2))
        for path in paths[1:]:
            (self.root / path).write_text("Original synthetic material.\n")
        self.entries = []
        for path in paths:
            content = (self.root / path).read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            self.entries.append({
                "source_path": path, "path": path,
                "source_sha256": digest, "sha256": digest,
                "bytes": len(content), "change": "Unchanged.",
            })

        self.expected_paths = frozenset((entry["source_path"], entry["path"]) for entry in self.entries)

    def refresh_notebook(self):
        content = json.dumps(self.notebook).encode()
        (self.root / "notebook.ipynb").write_bytes(content)
        entry = self.entries[0]
        entry.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
        entry["change"] = (
            "Unchanged." if entry["sha256"] == entry["source_sha256"]
            else "Documented synthetic notebook edit."
        )

    def result(self):
        (self.root / "docs/source-manifest.json").write_text(json.dumps({"files": self.entries}))
        stderr = io.StringIO()
        with patch("check_archive.EXPECTED_SOURCE_PATHS", self.expected_paths), redirect_stdout(io.StringIO()), redirect_stderr(stderr):
            status = check_archive(self.root)
        return status, stderr.getvalue()

    def assert_rejected(self, reason):
        status, errors = self.result()
        self.assertEqual(status, 1)
        self.assertIn(reason, errors)

    def test_valid_archive(self):
        self.assertEqual(self.result(), (0, ""))

    def test_student_id_assignments(self):
        for source in ["STUDENT_ID = 12345678", "STUDENT_ID = '12345678'", 'STUDENT_ID: str = "12345678"']:
            with self.subTest(source=source):
                self.notebook["cells"][0]["source"] = source
                self.refresh_notebook()
                self.assert_rejected("student identifier")

    def test_student_id_in_split_output(self):
        self.notebook["cells"][0]["outputs"] = [{
            "output_type": "stream", "name": "stdout",
            "text": ["Student ID: ", "12345678\n"],
        }]
        self.refresh_notebook()
        self.assert_rejected("student identifier")

    def test_student_id_in_metadata(self):
        self.notebook["metadata"] = {"student_id": 12345678}
        self.refresh_notebook()
        self.assert_rejected("student identifier")

    def test_grading_key_in_source(self):
        self.notebook["cells"][0]["source"] = "grader_api_key: 'synthetic-test-value'"
        self.refresh_notebook()
        self.assert_rejected("grading key")

    def test_grading_key_in_output_with_empty_source_key(self):
        self.notebook["cells"][0]["source"] = "grader_api_key: ''"
        for output in ["grader_api_key: 'synthetic-test-value'", "grader_api_key: synthetic-test-value"]:
            with self.subTest(output=output):
                self.notebook["cells"][0]["outputs"] = [{
                    "output_type": "stream", "name": "stdout", "text": output,
                }]
                self.refresh_notebook()
                self.assert_rejected("grading key")

    def test_grading_key_in_structured_output(self):
        self.notebook["cells"][0]["outputs"] = [{
            "output_type": "display_data", "metadata": {},
            "data": {"application/json": {"grader_api_key": "synthetic-test-value"}},
        }]
        self.refresh_notebook()
        self.assert_rejected("grading key")

    def test_empty_and_null_keys_are_allowed(self):
        self.notebook["cells"][0]["source"] = "grader_api_key = None\ngrader_api_key: null\ngrader_api_key = ''"
        self.notebook["cells"][0]["outputs"] = [{
            "output_type": "stream", "name": "stdout", "text": "grader_api_key: ''\n",
        }]
        self.refresh_notebook()
        self.assertEqual(self.result(), (0, ""))

    def test_changed_file_with_unchanged_claim(self):
        self.notebook["metadata"] = {"description": "Edited notebook"}
        self.refresh_notebook()
        self.entries[0]["change"] = "Unchanged."
        self.assert_rejected("Provenance claim")

    def test_unchanged_file_with_change_claim(self):
        self.entries[0]["change"] = "Changed the notebook."
        self.assert_rejected("Provenance claim")

    def test_documented_edit_is_allowed(self):
        self.notebook["metadata"] = {"description": "Edited notebook"}
        self.refresh_notebook()
        self.assertEqual(self.result(), (0, ""))

    def test_removing_file_and_manifest_entry(self):
        entry = self.entries.pop()
        (self.root / entry["path"]).unlink()
        self.assert_rejected("imported files; found")

    def test_duplicate_source_path(self):
        self.entries[1]["source_path"] = self.entries[0]["source_path"]
        self.assert_rejected("Duplicate source path")

    def test_same_count_replacement(self):
        entry = self.entries[-1]
        (self.root / entry["path"]).rename(self.root / "replacement.txt")
        entry.update(source_path="replacement.txt", path="replacement.txt")
        self.assert_rejected("fixed imported path inventory")

    def test_destination_mapping_change(self):
        entry = self.entries[-1]
        (self.root / entry["path"]).rename(self.root / "replacement.txt")
        entry["path"] = "replacement.txt"
        self.assert_rejected("fixed imported path inventory")

    def test_unlisted_notebook(self):
        self.notebook["cells"][0]["source"] = "Student ID: 12345678"
        (self.root / "added.ipynb").write_text(json.dumps(self.notebook))
        self.assert_rejected("student identifier")

    def test_prose_student_id(self):
        for location in ("source", "outputs", "metadata"):
            with self.subTest(location=location):
                cell = self.notebook["cells"][0]
                cell.update(source="", outputs=[], metadata={})
                cell[location] = "My student ID is 12345678"
                self.refresh_notebook()
                self.assert_rejected("student identifier")

    def test_bare_equals_grading_key(self):
        self.notebook["cells"][0]["source"] = "grader_api_key = synthetic-test-value"
        self.refresh_notebook()
        self.assert_rejected("grading key")

    def test_triple_quoted_grading_keys(self):
        for quotes in (chr(34) * 3, chr(39) * 3):
            for value in ("synthetic-test-value", "\nsynthetic-test-value\n"):
                with self.subTest(quotes=quotes, value=value):
                    self.notebook["cells"][0]["source"] = "grader_api_key = " + quotes + value + quotes
                    self.refresh_notebook()
                    self.assert_rejected("grading key")

    def test_hyphenated_student_label(self):
        self.notebook["cells"][0]["source"] = "Student-ID: 12345678"
        self.refresh_notebook()
        self.assert_rejected("student identifier")

    def test_case_variant_notebook_extensions(self):
        self.notebook["cells"][0]["source"] = "Student ID: 12345678"
        for suffix in (".IPYNB", ".IpYnB"):
            with self.subTest(suffix=suffix):
                path = self.root / ("added" + suffix)
                path.write_text(json.dumps(self.notebook))
                self.assert_rejected("student identifier")
                path.unlink()


if __name__ == "__main__":
    unittest.main()
