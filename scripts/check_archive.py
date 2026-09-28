"""Validate this archive with Python's standard library, without running project code."""

import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile


def check_archive(root):
    manifest = json.loads((root / "docs/source-manifest.json").read_text())
    failures = []
    imported_paths = set()
    for entry in manifest["files"]:
        relative = entry["path"]
        path = root / relative
        if relative in imported_paths:
            failures.append(f"Duplicate manifest path: {relative}")
        imported_paths.add(relative)
        if not path.resolve().is_relative_to(root.resolve()):
            failures.append(f"Manifest path outside repository: {relative}")
            continue
        if not path.is_file():
            failures.append(f"Missing imported file: {relative}")
            continue
        contents = path.read_bytes()
        if len(contents) != entry["bytes"]:
            failures.append(f"Size differs from manifest: {relative}")
        if hashlib.sha256(contents).hexdigest() != entry["sha256"]:
            failures.append(f"Hash differs from manifest: {relative}")
        try:
            if path.suffix == ".ipynb":
                notebook = json.loads(contents)
                if notebook.get("nbformat") != 4:
                    raise ValueError("expected notebook format 4")
                if not isinstance(notebook.get("cells"), list):
                    raise ValueError("missing notebook cell list")
                if re.search(r"Student ID:\s*\d{8}", json.dumps(notebook)):
                    raise ValueError("unredacted student identifier in notebook")
                for index, cell in enumerate(notebook["cells"]):
                    if cell.get("cell_type") not in {"markdown", "code", "raw"}:
                        raise ValueError(f"invalid cell type at cell {index}")
                    source = cell.get("source")
                    if not isinstance(source, (str, list)):
                        raise ValueError(f"missing source at cell {index}")
                    if isinstance(source, list) and not all(isinstance(line, str) for line in source):
                        raise ValueError(f"invalid source at cell {index}")
                    source_text = "".join(source) if isinstance(source, list) else source
                    if re.search(r"grader_api_key:\s*['\"][^'\"\n]+['\"]", source_text):
                        raise ValueError(f"embedded grading key at cell {index}")
            elif path.suffix == ".zip":
                with zipfile.ZipFile(path) as archive:
                    damaged = archive.testzip()
                    if damaged:
                        raise ValueError(f"damaged ZIP member: {damaged}")
            elif path.suffix == ".pdf" and not contents.startswith(b"%PDF-"):
                raise ValueError("missing PDF header")
        except (ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            failures.append(f"Invalid asset {relative}: {error}")

    python_files = sorted(root.rglob("*.py"))
    python_files = [path for path in python_files if path.relative_to(root).parts[0] not in {".venv", "venv", ".git"}]
    for path in python_files:
        try:
            ast.parse(path.read_bytes(), filename=str(path.relative_to(root)))
        except SyntaxError as error:
            failures.append(f"Python syntax: {path.relative_to(root)}: {error}")

    # Original course documentation may point to files outside the recovered archive.
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
    print(f"Archive checks passed: {len(imported_paths)} imported files, {len(python_files)} Python files, and {len(guides) - 1} guides.")
    return 0


if __name__ == "__main__":
    sys.exit(check_archive(Path(__file__).resolve().parents[1]))
