# Archive notes

The repository was prepared on September 28, 2026 from the `Projects-main` download. It uses a fresh Git history owned by `27kms`.

## Preserved material

All 67 files from the download are included. The project folder names remain unchanged, so paths between the original files still resolve as before. The original root README moved to `docs/original-readme.md`.

Reports, Python files, datasets, ZIP archives, HTML charts, and notebook outputs retain their original contents. Two notebook files have a narrowly scoped change:

| File | Change |
| --- | --- |
| `NLP/HW3/Notebook.ipynb` | Emptied the embedded `grader_api_key` value and replaced the student identifier in saved output with `XXXXXXXX`. |
| `NLP/HW4/Notebook.ipynb` | Emptied the embedded `grader_api_key` value and replaced the student identifier in saved output with `XXXXXXXX`. |

The historical grading service requires separately authorized course access. These empty values are deliberate.

The source manifest records both original and imported hashes. Unchanged files have matching hashes. `.gitattributes` disables automatic line-ending conversion to preserve these bytes across checkouts.

## Added repository files

The new overview and reproduction notes help readers navigate the archive. Ignore rules exclude local environments, caches, credentials, and generated grader configuration. Editor settings apply consistent defaults to future edits.

The archive-check script uses only Python's standard library. It enforces the 67-file inventory and checks that change descriptions agree with the original and imported hashes. It also checks notebook sources, saved outputs, and metadata for the grading identifiers and key formats used in these assignments.

Synthetic regression tests cover those safeguards. Run them with `python3 -m unittest discover -s scripts -p 'test_*.py'`.

The GitHub Actions workflow runs both checks using tools already present on the runner and downloads only this repository's source. It does not install dependencies or third-party actions.

## Ownership and reuse

Git commits for this import are attributed to `27kms`. The academic work includes course starter code, team deliverables, and cited third-party data. Their existing credits remain in place. This import does not assign a new license to the collection.
