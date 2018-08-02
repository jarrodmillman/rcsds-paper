""" Calculate github metrics for projects

Data read from:

* JSON file, abstracted via the Github API (``fetch_project_data.py``);
* cloc utility output from projects (``cloc_projects.sh``);
* Report for code coverage (``get_coveralls_reports.sh``).
"""

from os.path import join as pjoin
import re
import json
import datetime
from collections import OrderedDict

import pytz
import pandas as pd

from tabulate import tabulate

# Constants
DATA_FNAME = 'project_data.json'
ORG_NAME = 'berkeley-stat159'
INSTRUCTOR_LOGINS = ('rossbar', 'jarrodmillman', 'jbpoline', 'matthew-brett')
INSTRUCTOR_NAMES = ('Ross Barnowski',
                    'Jarrod Millman',
                    'Matthew Brett',
                    'Jean-Baptiste Poline')
# See: https://registrar.berkeley.edu/sites/default/files/pdf/UCB_AcademicCalendar_2015-16.pdf
TERM_END = datetime.datetime(2015, 12, 18, 23, 59, 59, 999, pytz.utc)


def load_data(fname=DATA_FNAME):
    """ Load stored JSON data from Github query

    Query in fetch_github_data.py
    """
    with open(fname, 'rt') as fobj:
        repos_d = json.load(fobj)
    del repos_d['project-aleph']  # Not started
    return repos_d


def get_issues_prs(issues_prs):
    """ Split generic `issues_prs` into actual issues and PRs
    """
    issues = [i for i in issues_prs if '/issues/' in i['html_url']]
    prs = [i for i in issues_prs if '/pull/' in i['html_url']]
    assert len(issues) + len(prs) == len(issues_prs)
    return issues, prs


def members_only(elements):
    """ Filter out elements created by instructors """
    return [e for e in elements if e['user']['login'] not in INSTRUCTOR_LOGINS]


def in_term(elements):
    """ Filter out elements after end of semester """
    return [e for e in elements if str2dt(e['created_at']) < TERM_END]


def valid(elements):
    return in_term(members_only(elements))


def valid_commits(commits):
    """ Filter commits by instructors, after end of term """
    valids = []
    for commit in commits:
        data = commit['commit']['author']
        if str2dt(data['date']) >= TERM_END:
            continue
        if data['name'] in INSTRUCTOR_NAMES:
            continue
        valids.append(commit)
    return valids


def get_comments(elements):
    return [e['comment_contents'] for e in elements]


def word_count(text):
    for char in ',.:;\'"`-@()':
        text = text.replace(char, ' ')
    return len(text.split())


def mean_wc(elements):
    n = len(elements)
    return sum(word_count(e['body']) for e in elements) / n if n else 0


def str2dt(dt_str):
     """ Convert Github data representation to datetime """
     naive = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%XZ')
     return pytz.utc.localize(naive)


def get_metrics(repo):
    """ Calculate dictionary of metrics from repository dict """
    m = OrderedDict()
    m['Commits'] = len(valid_commits(repo['commits']))
    issues, prs = get_issues_prs(repo['issues'])
    issues_prs = issues + prs
    comments = valid(sum(get_comments(issues_prs), []))
    m['Issues'] = len(valid(issues))
    m['PRs'] = len(valid(prs))
    m['Comments'] = len(comments)
    m['Words/comment'] = mean_wc(comments)
    return m


def metrics_df(repos):
    """ Create metrics dataframe from repositories dict """
    dicts = [get_metrics(repo) for repo in repos.values()]
    names = [name.split('-')[1].capitalize() for name in repos]
    return pd.DataFrame(dicts, index=names)


# Splitter for processing cloc_output.txt file.  This contains the output of
# the cloc runs on the project repositories.
PROJECT_RE = re.compile('^Analyzing', flags=re.M)
CLOC_RE = re.compile('^github.com/AlDanial/cloc', flags=re.M)


def ana_project(proj_part):
    """ Process cloc outputs for one repository """
    name = proj_part.splitlines()[0].strip()
    clocs = CLOC_RE.split(proj_part)[1:]
    counts = [ana_cloc(c) for c in clocs if c]
    return name, dict(zip(['LoC', 'no_tests', 'no_tests_scripts'], counts))


def ana_cloc(cloc_part):
    """ Process output from single cloc run """
    for line in cloc_part.splitlines():
        if not line.startswith('SUM:'):
            continue
        return int(line.split()[-1])


def cloc_df(fname):
    """ Create dataframe by processing cloc output in `fname`
    """
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    proj_dicts = []
    proj_names = []
    for proj_part in PROJECT_RE.split(contents):
        if proj_part.strip() == '':
            continue
        name, values = ana_project(proj_part)
        proj_names.append(name.capitalize())
        proj_dicts.append(values)
    df = pd.DataFrame(proj_dicts, index=proj_names)
    proc_df = pd.DataFrame()
    proc_df = df[['LoC', 'no_tests']].copy()
    return proc_df

# Coveralls report parsing
LINES_RE = re.compile(r"<strong>(\d+)</strong>")

def get_lines_covered(report_file):
    with open(report_file, 'rt') as fobj:
        lines = fobj.read().splitlines()
    index = lines.index("<label>Run Details</label>")
    assert index != -1
    covered = lines[index + 2]
    match = LINES_RE.match(covered)
    if match:
        return int(match.groups()[0])


# Load JSON data stored from Github queries.
repos = load_data()
# Calculate metrics from Github queries.
df1 = metrics_df(repos)
# Calculate metrics from cloc output file.
df2 = cloc_df('cloc_output.txt')
# Calculate coverage
covered = {p: get_lines_covered(pjoin('coveralls-reports', p.lower() + '-report.html'))
           for p in df1.index}
df2["% covered"] = pd.Series(covered) / df2['no_tests'] * 100
df2 = df2.drop(columns='no_tests')
# Merge into single data frame
df = pd.concat([df1, df2], axis=1)
# Duplicate index as new column at beginning of data frame.  This makes it
# easier to display the project names with a column heading.
df.insert(0, 'Project', df.index)
# Create, print LaTeX table from dataframe.
table = tabulate(df, tablefmt="latex", floatfmt=".1f", headers='keys',
                 showindex='never')
print(table)
