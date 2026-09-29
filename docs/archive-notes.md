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

The archive-check script uses only Python's standard library. It verifies the 67 preserved files against the approved import baseline and checks that change descriptions agree with the original and imported hashes.

Synthetic regression tests cover those safeguards. Run them with `python3 -m unittest discover -s scripts -p 'test_*.py'`.

The GitHub Actions workflow runs both checks using tools already present on the runner and downloads only this repository's source. It does not install dependencies or third-party actions.

## Ownership and reuse

Git commits for this import are attributed to `27kms`. The academic work includes course starter code, team deliverables, and cited third-party data. Their existing credits remain in place. This import does not assign a new license to the collection.

## Preservation contract

`scripts/approved-imports.json` fixes the reviewed source paths, destination paths, original hashes, imported hashes, and sizes. It was established by comparing the import with the downloaded files. The checker requires the manifest to match this independent baseline and imported bytes to match the approved hashes. Editing the manifest alone cannot authorize an archive change.

These are preserved snapshots. Any change to an imported notebook, including restoring a redacted value in any syntax or location, fails its hash check. Additional notebooks are rejected, including case variants of `.ipynb`. Local `.git`, `.venv`, `venv`, and `.ipynb_checkpoints` directories are excluded. Documentation and maintenance scripts may still be edited.

The checker does not assess arbitrary notebook content for secrets. An intentional future archive revision requires a separately reviewed baseline update and a fresh content review. The baseline is a repository invariant, not protection against someone deliberately changing both the baseline and validator.
