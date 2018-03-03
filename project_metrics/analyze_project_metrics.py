""" Analyze project metrics
"""

from os.path import dirname, join as pjoin
import re

import numpy as np

import pandas as pd

HERE = dirname(__file__)

statements_per_line = np.mean([0.7, 0.9, 0.95])

with open(pjoin(HERE, 'project_metrics.md'), 'rt') as fobj:
    contents = fobj.read()

project_name_re = re.compile('^[A-Za-z]+$', flags=re.M)
projects = project_name_re.split(contents)
assert len(projects) == 12  # includes header
project_names = project_name_re.findall(contents)
assert len(project_names) == 11

# Drop heading
projects = projects[1:]

columns = ['name', 'all', 'wo_tests', 'wo_tests_scripts', 'found_statements',
           'percent_found_covered', 'prs', 'issues']
dtypes = {'name': 'object', 'percent_found_covered': 'float64'}
dtypes.update({name: 'int64' for name in columns if name not in dtypes})
df = pd.DataFrame(columns=columns)
# all, wo-tests, wo-tests-scripts, found-statements, percent-found-covered
values = []
for project in projects:
    values.append([int(v) for v in project.split()])
df['name'] = project_names
df.iloc[:, 1:] = values
df['test_lines'] = (df['all'] - df['wo_tests']).astype(float)
df = df.astype(dtype=dtypes)
df['est_lines_covered'] = (df['found_statements'] / statements_per_line
                           * df['percent_found_covered'] / 100)
df['estimated_coverage'] = df['est_lines_covered'] / df['wo_tests'] * 100
summary = pd.DataFrame([df.median(), df.min(), df.max()])

print(summary)
