#!/bin/bash
# Get coverage reports from coveralls
# Need to be logged into Coveralls to get anything not more or less blank.
PROJECTS="alpha beta delta epsilon eta gamma iota kappa lambda theta zeta"
mkdir -p coveralls-reports
for project in $PROJECTS; do
    curl -L -o coveralls-reports/$project-report.html  https://coveralls.io/github/berkeley-stat159/project-$project
done
# For some reason, project betas builds broke at the end.  Use an older one.
curl -L -o coveralls-reports/beta-report.html  https://coveralls.io/builds/4460178
