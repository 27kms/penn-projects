# Penn projects

University of Pennsylvania coursework and research by [27kms](https://github.com/27kms), covering language models, sports analytics, interactive fiction, and applied probability.

This archive preserves the submitted reports, notebooks, code, and supporting data. It records historical work. The notebooks have not been rerun against current libraries.

## Explore the projects

| Project | Focus | Start here |
| --- | --- | --- |
| Applied probability | Negative binomial modeling of MLB triples for Peter Fader's Applied Probability Models in Marketing course | [Paper](Applied_Probability_Models_in_Marketing/Project1/Report.pdf) |
| Capstone | Matching Men's Health articles with relevant products, in conjunction with Wharton Analytics Fellows | [Capstone paper](Capstone/Hearst_Capstone_Paper.pdf) |
| Interactive fiction | Text adventure games and language-model-assisted game development | [Action Castle notebook](Interactive_Fiction/action_castle.ipynb) · [Project report](Interactive_Fiction/Report.md) |
| March Madness | Early Bayesian basketball prediction models and exploratory visualizations | [Modeling notebook](March_Madness/NCAA_BB.ipynb) · [Charts](March_Madness/Graphs/) |
| Natural language processing | Part-of-speech tagging, course assignments, and a collaborative study of gender in tennis journalism | [POS tagger](NLP/HW2/Code/pos_tagger.py) · [Tennis project](NLP/Final_Project/README.md) · [Paper](NLP/Final_Project/Deliverables/Report.pdf) |
| WAF data challenge | Horse-racing data exploration and prediction for a time-limited interview challenge | [Notebook](WAF_Data_Challenge/Notebook.ipynb) · [Presentation](WAF_Data_Challenge/Presentation.pdf) |

## Use the archive

GitHub displays the notebooks and PDFs directly. Download the HTML charts in `March_Madness/Graphs/` to view their interactive plots locally.

The projects have separate environments and missing external inputs. Read the [reproduction notes](docs/reproduction.md) before running code. Original notebook outputs remain as historical results, with the student identifier redacted. Embedded course grading keys were also removed.

Run the archive checks with an existing Python 3.11 or newer installation:

```sh
python3 scripts/check_archive.py
```

The checks verify imported file hashes, Python source syntax, notebook structure, ZIP integrity, and local links in the new guides. They do not execute the experiments or install packages.

## Preservation and credits

The [archive notes](docs/archive-notes.md) explain the import. The [source manifest](docs/source-manifest.json) records every imported file and its SHA-256 hash. The [original overview](docs/original-readme.md) is also preserved.

Course starter code, team contributions, and third-party materials retain the credits in their original files. No new license is granted for those materials.

Related archive: [AMU mathematics projects](https://github.com/27kms/amu-projects).
