# Project analysis

Also see `project_metrics.md` and `Makefile`.

`github_metrics.py` is the main analysis script generating table 2 in the
paper.   You should be able to run that script from this directory, and get
the same output as we have in the paper.

We have already downloaded and committed Github metadata from the
repositories, as `project_data.json`.  If you want to check this, run

```
python fetch_project_data.py your-gh-username your-gh-password
```

The repository data is all public, but you'll need your Github login in order
to allow the large number of queries that this script generates.

``github_metrics.py`` also uses the output from multiple runs of the `cloc`
utility, on each project.  The output is in ``cloc_output.txt``.  You should
be able to replicate this file, with:

```
bash clone_projects.sh
```

to clone all the student project directories to the current directory,
followed by:

```
bash cloc_projects.sh > cloc_output.txt
```

We used coverage statistics from [coveralls](https://coveralls.io).  See `get_coveralls_reports.sh` for script to download the Coveralls report for each project.  We analyze these in `github_metrics.py`.
