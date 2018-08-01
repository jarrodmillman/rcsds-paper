#!/bin/bash
# See clone_projects.sh
PROJECTS="alpha beta delta epsilon eta gamma iota kappa lambda theta zeta"
for project in $PROJECTS; do
    git clone https://github.com/berkeley-stat159/project-$project
done
