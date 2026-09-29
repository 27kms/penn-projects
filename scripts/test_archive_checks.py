"""Exercise preservation guarantees with synthetic files, not historical data."""

from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from check_archive import check_archive


class ArchiveChecksTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text("# Archive\n")
        (self.root / "docs/original-readme.md").write_text("Historical README\n")
        notebook = {"nbformat": 4, "cells": [{"cell_type": "code", "source": "STUDENT_ID = 'XXXXXXXX'"}]}
        (self.root / "notebook.ipynb").write_text(json.dumps(notebook))
        self.entries = []
        for source, target in (("README.md", "docs/original-readme.md"), ("notebook.ipynb", "notebook.ipynb")):
            content = (self.root / target).read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            self.entries.append(dict(source_path=source, path=target, source_sha256=digest,
                                     sha256=digest, bytes=len(content), change="Unchanged."))
        self.approved = copy.deepcopy(self.entries)

    def result(self):
        (self.root / "docs/source-manifest.json").write_text(json.dumps({"files": self.entries}))
        errors = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(errors):
            status = check_archive(self.root, approved=self.approved)
        return status, errors.getvalue()

    def assert_rejected(self, reason):
        status, errors = self.result()
        self.assertEqual(status, 1)
        self.assertIn(reason, errors)

    def test_approved_imports_pass(self):
        self.assertEqual(self.result(), (0, ""))

    def test_changed_bytes_and_updated_manifest_fail(self):
        entry = self.entries[1]
        path = self.root / entry["path"]
        path.write_text(path.read_text().replace("XXXXXXXX", "12345678"))
        content = path.read_bytes()
        entry.update(sha256=hashlib.sha256(content).hexdigest(), bytes=len(content), change="Changed notebook.")
        self.assert_rejected("Imported bytes differ")
        self.assert_rejected("Manifest differs")

    def test_same_count_replacement_fails(self):
        entry = self.entries[0]
        (self.root / entry["path"]).rename(self.root / "replacement.txt")
        entry.update(source_path="replacement.txt", path="replacement.txt")
        self.assert_rejected("Manifest differs")
        self.assert_rejected("Missing imported file")

    def test_source_hash_or_mapping_change_fails(self):
        for field, value in (("source_sha256", "0" * 64), ("source_path", "different.md"), ("path", "README.md")):
            with self.subTest(field=field):
                self.entries = copy.deepcopy(self.approved)
                self.entries[0][field] = value
                self.assert_rejected("Manifest differs")

    def test_missing_or_duplicate_entry_fails(self):
        self.entries.pop()
        self.assert_rejected("Manifest differs")
        self.entries = copy.deepcopy(self.approved)
        self.entries.append(copy.deepcopy(self.entries[0]))
        self.assert_rejected("Manifest differs")

    def test_new_notebooks_fail_regardless_of_case(self):
        for extension in (".ipynb", ".IPYNB", ".IpYnB"):
            with self.subTest(extension=extension):
                path = self.root / ("added" + extension)
                path.write_bytes((self.root / "notebook.ipynb").read_bytes())
                self.assert_rejected("Notebook outside approved archive")
                path.unlink()

    def test_local_notebook_checkpoints_are_ignored(self):
        folder = self.root / "nested/.ipynb_checkpoints"
        folder.mkdir(parents=True)
        (folder / "checkpoint.ipynb").write_text("Local stale notebook")
        self.assertEqual(self.result(), (0, ""))

    def test_added_documentation_is_allowed(self):
        (self.root / "docs/new-guide.md").write_text("# New guide\n")
        self.assertEqual(self.result(), (0, ""))

    def test_broken_documentation_link_fails(self):
        (self.root / "README.md").write_text("[Missing](missing.txt)\n")
        self.assert_rejected("Broken local link")

    def test_provenance_contradiction_fails(self):
        self.entries[0]["change"] = "Changed the file."
        self.assert_rejected("Provenance claim")


if __name__ == "__main__":
    unittest.main()
