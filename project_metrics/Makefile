GH_USER ?= matthew-brett
GH_PASSWORD ?= my-password

analysis:
	python analyze_project_metrics.py

collect-gh-data:
	python fetch_project_data.py $(GH_USER) $(GH_PASSWORD)

cloc-output:
	bash clone_projects.sh
	bash cloc_projects.sh > cloc_output.txt

analyze-gh-data: collect-gh-data cloc-output
	python github_metrics.py
