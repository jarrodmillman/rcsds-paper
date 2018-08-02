#!/bin/bash
# Count lines of code for projects
PROJECTS="alpha beta delta epsilon eta gamma iota kappa lambda theta zeta"
for project in $PROJECTS; do
    echo "Analyzing $project"
    cloc --include-lang=Python project-$project
    cloc --include-lang=Python --exclude-dir=tests project-$project
    cloc --include-lang=Python --exclude-dir=tests,scripts project-$project
done
