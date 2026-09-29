"""Verify a preserved archive against its independently reviewed import baseline."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile


BASELINE_PATH = Path(__file__).with_name("approved-imports.json")
FIELDS = ("source_path", "path", "source_sha256", "sha256", "bytes")


def check_archive(root, approved=None):
    if approved is None:
        approved = json.loads(BASELINE_PATH.read_text())["files"]
    manifest = json.loads((root / "docs/source-manifest.json").read_text())["files"]
    failures = []
    expected = Counter(tuple(entry[field] for field in FIELDS) for entry in approved)
    actual = Counter(tuple(entry[field] for field in FIELDS) for entry in manifest)
    if actual != expected:
        failures.append("Manifest differs from the approved import baseline.")
    for entry in manifest:
        unchanged = entry["change"].strip().lower().rstrip(".") == "unchanged"
        if not entry["change"].strip() or unchanged != (entry["source_sha256"] == entry["sha256"]):
            failures.append(f"Provenance claim contradicts recorded hashes: {entry['path']}")

    for entry in approved:
        relative = entry["path"]
        path = root / relative
        if not path.resolve().is_relative_to(root.resolve()):
            failures.append(f"Imported path outside repository: {relative}")
            continue
        if not path.is_file():
            failures.append(f"Missing imported file: {relative}")
            continue
        contents = path.read_bytes()
        if len(contents) != entry["bytes"] or hashlib.sha256(contents).hexdigest() != entry["sha256"]:
            failures.append(f"Imported bytes differ from approved baseline: {relative}")
        try:
            if path.suffix.lower() == ".ipynb":
                notebook = json.loads(contents)
                if not isinstance(notebook, dict) or notebook.get("nbformat") != 4:
                    raise ValueError("expected notebook format 4")
                if not isinstance(notebook.get("cells"), list):
                    raise ValueError("missing notebook cell list")
                for index, cell in enumerate(notebook["cells"]):
                    if not isinstance(cell, dict) or cell.get("cell_type") not in {"markdown", "code", "raw"}:
                        raise ValueError(f"invalid cell type at cell {index}")
                    source = cell.get("source")
                    if not isinstance(source, (str, list)) or (
                        isinstance(source, list) and not all(isinstance(line, str) for line in source)
                    ):
                        raise ValueError(f"invalid source at cell {index}")
            elif path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    damaged = archive.testzip()
                    if damaged:
                        raise ValueError(f"damaged ZIP member: {damaged}")
            elif path.suffix.lower() == ".pdf" and not contents.startswith(b"%PDF-"):
                raise ValueError("missing PDF header")
        except (ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            failures.append(f"Invalid asset {relative}: {error}")

    files = sorted(path for path in root.rglob("*") if path.is_file()
                   and not {".git", ".venv", "venv", ".ipynb_checkpoints"}.intersection(path.relative_to(root).parts))
    approved_notebooks = {entry["path"] for entry in approved if Path(entry["path"]).suffix.lower() == ".ipynb"}
    for path in files:
        relative = str(path.relative_to(root))
        if path.suffix.lower() == ".ipynb" and relative not in approved_notebooks:
            failures.append(f"Notebook outside approved archive: {relative}")
        if path.suffix == ".py":
            try:
                ast.parse(path.read_bytes(), filename=relative)
            except SyntaxError as error:
                failures.append(f"Python syntax: {relative}: {error}")

    # Historical documentation may point outside the recovered download.
    guides = [root / "README.md", *(root / "docs").glob("*.md")]
    for guide in guides:
        if guide.name == "original-readme.md":
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", guide.read_text()):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            if not (guide.parent / unquote(url.path)).exists():
                failures.append(f"Broken local link in {guide.relative_to(root)}: {target}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Archive checks passed: {len(approved)} approved imported files.")
    return 0


if __name__ == "__main__":
    sys.exit(check_archive(Path(__file__).resolve().parents[1]))
