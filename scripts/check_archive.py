"""Validate this archive with Python's standard library, without running project code."""

import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile


EXPECTED_SOURCE_PATHS = frozenset({
    ('Applied_Probability_Models_in_Marketing/Project1/Report.pdf', 'Applied_Probability_Models_in_Marketing/Project1/Report.pdf'),
    ('Capstone/Hearst_Capstone_Paper.pdf', 'Capstone/Hearst_Capstone_Paper.pdf'),
    ('Interactive_Fiction/README.md', 'Interactive_Fiction/README.md'),
    ('Interactive_Fiction/Report.md', 'Interactive_Fiction/Report.md'),
    ('Interactive_Fiction/__init__.py', 'Interactive_Fiction/__init__.py'),
    ('Interactive_Fiction/action_castle.ipynb', 'Interactive_Fiction/action_castle.ipynb'),
    ('Interactive_Fiction/actions/__init__.py', 'Interactive_Fiction/actions/__init__.py'),
    ('Interactive_Fiction/actions/base.py', 'Interactive_Fiction/actions/base.py'),
    ('Interactive_Fiction/actions/consume.py', 'Interactive_Fiction/actions/consume.py'),
    ('Interactive_Fiction/actions/fight.py', 'Interactive_Fiction/actions/fight.py'),
    ('Interactive_Fiction/actions/fish.py', 'Interactive_Fiction/actions/fish.py'),
    ('Interactive_Fiction/actions/locations.py', 'Interactive_Fiction/actions/locations.py'),
    ('Interactive_Fiction/actions/rose.py', 'Interactive_Fiction/actions/rose.py'),
    ('Interactive_Fiction/actions/things.py', 'Interactive_Fiction/actions/things.py'),
    ('Interactive_Fiction/blocks/__init__.py', 'Interactive_Fiction/blocks/__init__.py'),
    ('Interactive_Fiction/blocks/base.py', 'Interactive_Fiction/blocks/base.py'),
    ('Interactive_Fiction/blocks/doors.py', 'Interactive_Fiction/blocks/doors.py'),
    ('Interactive_Fiction/games.py', 'Interactive_Fiction/games.py'),
    ('Interactive_Fiction/hw2.ipynb', 'Interactive_Fiction/hw2.ipynb'),
    ('Interactive_Fiction/parsing.py', 'Interactive_Fiction/parsing.py'),
    ('Interactive_Fiction/things/__init__.py', 'Interactive_Fiction/things/__init__.py'),
    ('Interactive_Fiction/things/base.py', 'Interactive_Fiction/things/base.py'),
    ('Interactive_Fiction/things/characters.py', 'Interactive_Fiction/things/characters.py'),
    ('Interactive_Fiction/things/items.py', 'Interactive_Fiction/things/items.py'),
    ('Interactive_Fiction/things/locations.py', 'Interactive_Fiction/things/locations.py'),
    ('Interactive_Fiction/viz.py', 'Interactive_Fiction/viz.py'),
    ('March_Madness/2019_BB.ipynb', 'March_Madness/2019_BB.ipynb'),
    ('March_Madness/BB_solver.py', 'March_Madness/BB_solver.py'),
    ('March_Madness/Graphs/BarGraph1.html', 'March_Madness/Graphs/BarGraph1.html'),
    ('March_Madness/Graphs/BarGraph2.html', 'March_Madness/Graphs/BarGraph2.html'),
    ('March_Madness/Graphs/Heatmap.html', 'March_Madness/Graphs/Heatmap.html'),
    ('March_Madness/Graphs/Scatterplot.html', 'March_Madness/Graphs/Scatterplot.html'),
    ('March_Madness/Graphs/Scatterplot3D.html', 'March_Madness/Graphs/Scatterplot3D.html'),
    ('March_Madness/Graphs/ScatterplotGeo.html', 'March_Madness/Graphs/ScatterplotGeo.html'),
    ('March_Madness/Graphs/ScatterplotSeeds.html', 'March_Madness/Graphs/ScatterplotSeeds.html'),
    ('March_Madness/NCAA_BB.ipynb', 'March_Madness/NCAA_BB.ipynb'),
    ('March_Madness/README.md', 'March_Madness/README.md'),
    ('March_Madness/Wrangling.ipynb', 'March_Madness/Wrangling.ipynb'),
    ('NLP/Final_Project/Code/Project Notebook.ipynb', 'NLP/Final_Project/Code/Project Notebook.ipynb'),
    ('NLP/Final_Project/Data/Locations.zip', 'NLP/Final_Project/Data/Locations.zip'),
    ('NLP/Final_Project/Data/Names.zip', 'NLP/Final_Project/Data/Names.zip'),
    ('NLP/Final_Project/Data/Stock_Gender_Images.zip', 'NLP/Final_Project/Data/Stock_Gender_Images.zip'),
    ('NLP/Final_Project/Data/Tennis_Data.zip', 'NLP/Final_Project/Data/Tennis_Data.zip'),
    ('NLP/Final_Project/Deliverables/Presentation.pdf', 'NLP/Final_Project/Deliverables/Presentation.pdf'),
    ('NLP/Final_Project/Deliverables/Report.pdf', 'NLP/Final_Project/Deliverables/Report.pdf'),
    ('NLP/Final_Project/README.md', 'NLP/Final_Project/README.md'),
    ('NLP/HW2/Code/constants.py', 'NLP/HW2/Code/constants.py'),
    ('NLP/HW2/Code/evaluate.py', 'NLP/HW2/Code/evaluate.py'),
    ('NLP/HW2/Code/pos_tagger.py', 'NLP/HW2/Code/pos_tagger.py'),
    ('NLP/HW2/Code/utils.py', 'NLP/HW2/Code/utils.py'),
    ('NLP/HW2/Data/dev_x.csv', 'NLP/HW2/Data/dev_x.csv'),
    ('NLP/HW2/Data/dev_y.csv', 'NLP/HW2/Data/dev_y.csv'),
    ('NLP/HW2/Data/test_x.csv', 'NLP/HW2/Data/test_x.csv'),
    ('NLP/HW2/Data/tokens_w_unk_4.csv', 'NLP/HW2/Data/tokens_w_unk_4.csv'),
    ('NLP/HW2/Data/train_x.csv', 'NLP/HW2/Data/train_x.csv'),
    ('NLP/HW2/Data/train_y.csv', 'NLP/HW2/Data/train_y.csv'),
    ('NLP/HW2/README.md', 'NLP/HW2/README.md'),
    ('NLP/HW2/Report.pdf', 'NLP/HW2/Report.pdf'),
    ('NLP/HW2/requirements.txt', 'NLP/HW2/requirements.txt'),
    ('NLP/HW3/Notebook.ipynb', 'NLP/HW3/Notebook.ipynb'),
    ('NLP/HW3/Report.pdf', 'NLP/HW3/Report.pdf'),
    ('NLP/HW4/Notebook.ipynb', 'NLP/HW4/Notebook.ipynb'),
    ('README.md', 'docs/original-readme.md'),
    ('WAF_Data_Challenge/Data/races.csv', 'WAF_Data_Challenge/Data/races.csv'),
    ('WAF_Data_Challenge/Data/runs.csv', 'WAF_Data_Challenge/Data/runs.csv'),
    ('WAF_Data_Challenge/Notebook.ipynb', 'WAF_Data_Challenge/Notebook.ipynb'),
    ('WAF_Data_Challenge/Presentation.pdf', 'WAF_Data_Challenge/Presentation.pdf'),
})
EXPECTED_SOURCE_COUNT = len(EXPECTED_SOURCE_PATHS)


def notebook_strings(value):
    """Read text from sources, outputs, and metadata, including split text arrays."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            yield "".join(value)
        else:
            for item in value:
                yield from notebook_strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"student_id", "grader_api_key"} and isinstance(item, (str, int)):
                yield f"{key}: {item}"
            yield from notebook_strings(item)


def check_notebook_privacy(notebook):
    student_id = re.compile(
        r"\bstudent[ _-]+id\b[^\r\n]*\b\d{8}\b",
        re.IGNORECASE,
    )
    grading_key = re.compile(
        r"\bgrader_api_key['\"]?[ \t]*[:=][ \t]*(?P<value>[^\r\n]*)",
        re.IGNORECASE,
    )
    empty_key = re.compile(r"(?:''|\"\"|null|None|~)?[ \t]*(?:#.*)?")
    for text in notebook_strings(notebook):
        if student_id.search(text):
            raise ValueError("unredacted student identifier in notebook")
        for match in grading_key.finditer(text):
            if not empty_key.fullmatch(match.group("value")):
                raise ValueError("embedded grading key in notebook")


def check_archive(root):
    manifest = json.loads((root / "docs/source-manifest.json").read_text())
    failures = []
    if len(manifest["files"]) != EXPECTED_SOURCE_COUNT:
        failures.append(f"Expected {EXPECTED_SOURCE_COUNT} imported files; found {len(manifest['files'])}.")
    actual_paths = {(entry["source_path"], entry["path"]) for entry in manifest["files"]}
    if actual_paths != EXPECTED_SOURCE_PATHS:
        failures.append("Manifest differs from the fixed imported path inventory.")
    imported_paths = set()
    source_paths = set()
    for entry in manifest["files"]:
        relative = entry["path"]
        path = root / relative
        if relative in imported_paths:
            failures.append(f"Duplicate manifest path: {relative}")
        imported_paths.add(relative)
        if entry["source_path"] in source_paths:
            failures.append(f"Duplicate source path: {entry['source_path']}")
        source_paths.add(entry["source_path"])
        source_hash = entry["source_sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", source_hash):
            failures.append(f"Invalid source hash: {relative}")
        change = entry["change"].strip()
        claims_unchanged = change.lower().rstrip(".") == "unchanged"
        hashes_match = source_hash == entry["sha256"]
        if not change or claims_unchanged != hashes_match:
            failures.append(f"Provenance claim contradicts source and imported hashes: {relative}")
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
            if path.suffix == ".zip":
                with zipfile.ZipFile(path) as archive:
                    damaged = archive.testzip()
                    if damaged:
                        raise ValueError(f"damaged ZIP member: {damaged}")
            elif path.suffix == ".pdf" and not contents.startswith(b"%PDF-"):
                raise ValueError("missing PDF header")
        except (ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
            failures.append(f"Invalid asset {relative}: {error}")

    def repository_files(pattern):
        return sorted(path for path in root.rglob(pattern)
                      if not {".git", ".venv", "venv"}.intersection(path.relative_to(root).parts))

    for path in repository_files("*"):
        if path.suffix.lower() != ".ipynb" or not path.is_file():
            continue
        try:
            notebook = json.loads(path.read_bytes())
            if notebook.get("nbformat") != 4:
                raise ValueError("expected notebook format 4")
            if not isinstance(notebook.get("cells"), list):
                raise ValueError("missing notebook cell list")
            check_notebook_privacy(notebook)
            for index, cell in enumerate(notebook["cells"]):
                if cell.get("cell_type") not in {"markdown", "code", "raw"}:
                    raise ValueError(f"invalid cell type at cell {index}")
                source = cell.get("source")
                if not isinstance(source, (str, list)):
                    raise ValueError(f"missing source at cell {index}")
                if isinstance(source, list) and not all(isinstance(line, str) for line in source):
                    raise ValueError(f"invalid source at cell {index}")
        except (ValueError, KeyError, TypeError) as error:
            failures.append(f"Invalid notebook {path.relative_to(root)}: {error}")

    python_files = repository_files("*.py")
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
