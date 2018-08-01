""" Calculate github metrics for projects

Data read from JSON file, abstracted via the Github API.

See fetch_project_data.py.
"""

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
    with open(fname, 'rt') as fobj:
        repos_d = json.load(fobj)
    del repos_d['project-aleph']  # Not started
    return repos_d


def get_issues_prs(repo_d):
    issues_prs = repo_d['issues']
    issues = [i for i in issues_prs if '/issues/' in i['html_url']]
    prs = [i for i in issues_prs if '/pull/' in i['html_url']]
    assert len(issues) + len(prs) == len(issues_prs)
    return issues, prs


def members_only(elements):
    return [e for e in elements if e['user']['login'] not in INSTRUCTOR_LOGINS]


def in_term(elements):
    return [e for e in elements if str2dt(e['created_at']) < TERM_END]


def valid(elements):
    return in_term(members_only(elements))


def valid_commits(commits):
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
        text = text.replace(char, '')
    return len(text.split())


def mean_wc(elements):
    n = len(elements)
    return sum(word_count(e['body']) for e in elements) / n if n else 0


def str2dt(dt_str):
     naive = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%XZ')
     return pytz.utc.localize(naive)


def get_metrics(repo):
    m = OrderedDict()
    m['Commits'] = len(valid_commits(repo['commits']))
    issues, prs = get_issues_prs(repo)
    issues_prs = issues + prs
    comments = valid(sum(get_comments(issues_prs), []))
    m['Issues'] = len(valid(issues))
    m['PRs'] = len(valid(prs))
    m['Comments'] = len(comments)
    m['Words / comment'] = mean_wc(comments)
    return m


def metrics_df(repos):
    dicts = [get_metrics(repo) for repo in repos.values()]
    names = [name.split('-')[1].capitalize() for name in repos]
    return pd.DataFrame(dicts, index=names)


PROJECT_RE = re.compile('^Analyzing', flags=re.M)
CLOC_RE = re.compile('^github.com/AlDanial/cloc', flags=re.M)


def ana_project(proj_part):
    name = proj_part.splitlines()[0].strip()
    clocs = CLOC_RE.split(proj_part)[1:]
    counts = [ana_cloc(c) for c in clocs if c]
    return name, dict(zip(['LoC', 'no_tests', 'no_tests_scripts'], counts))


def ana_cloc(cloc_part):
    for line in cloc_part.splitlines():
        if not line.startswith('SUM:'):
            continue
        return int(line.split()[-1])


def cloc_df(fname):
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
    proc_df = df[['LoC']].copy()
    proc_df['Test LoC'] = df['LoC'] - df['no_tests']
    return proc_df


repos = load_data()
df1 = metrics_df(repos)
df2 = cloc_df('cloc_output.txt')
df = pd.concat([df1, df2], axis=1)
df.insert(0, 'Project', df.index)
table = tabulate(df, tablefmt="latex", floatfmt=".1f", headers='keys',
                 showindex='never')
print(table)
