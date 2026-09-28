# Reproduction notes

This collection has no shared runtime or complete dependency lockfile. The import preserves the historical implementations and outputs. It does not establish that the projects run end to end today.

## Project requirements and gaps

| Project | Surviving materials | Known gaps |
| --- | --- | --- |
| Applied probability | PDF report | Executable analysis and source data are absent from this download. |
| Capstone | PDF report | Application code and its runtime are absent. |
| Interactive fiction | Python modules and two notebooks | Notebooks expect a `text_adventure_games` package and, for homework 2, `hw1_solution`. The referenced package metadata and homework solution are absent. Graphviz and the historical OpenAI client also need separate setup. |
| March Madness | Solver, three notebooks, and exported plots | Notebooks reference local data outside this repository, Google Colab uploads, and packages including `aia`. The expected source data and complete environment are absent. |
| NLP homework 2 | POS tagger, CSV data, report, and historical requirements | The requirements file is only partially version-pinned. Confirm data paths relative to the working directory before running it. |
| NLP homework 3 and 4 | Course notebooks, plus the homework 3 report | Course grading services, external model or dataset downloads, and library versions need reconstruction. Embedded grading keys and the saved student identifier were redacted. |
| NLP final project | Notebook, reports, and four data archives | Absolute paths, external lexicons and vectors, and the original environment need reconstruction. ZIP files include their original macOS metadata. |
| WAF data challenge | Notebook, presentation, and two CSV files | The notebook reads `races.csv` and `runs.csv` from its working directory. The files are stored under `WAF_Data_Challenge/Data/`. Point those reads at `Data/` before running from the project folder. |

Original assignment READMEs describe their original course setup. Some commands refer to packaging files that are absent here. They are historical documentation.

## Dependency policy

The repository's `uv.toml` excludes package artifacts uploaded after September 21, 2026 at 00:00 UTC and disables automatic Python downloads. This fixed cutoff is at least seven days before the import date and remains conservative for later use. The RFC 3339 timestamp also works with older uv versions that cannot parse relative durations.

Use an already installed Python and a separate virtual environment for each project you reconstruct. If you advance the cutoff, keep it at least seven days before the time of resolution or installation.

When using uv from another directory, pass `--config-file /absolute/path/to/penn-projects/uv.toml` so the same policy applies. This configuration governs uv only. Historical notebook cells that call pip, download models, or clone external repositories do not inherit it. Review those cells before execution and use the applicable download tool's release-age control.

No dependencies were downloaded, resolved, or installed as part of this import.

## Validate the preserved files

From the repository root, run:

```sh
python3 scripts/check_archive.py
```

The command checks archive integrity without importing project modules, running notebook cells, contacting external services, or training models. Hash failures indicate that an imported file changed. Review the change before updating its manifest entry.
