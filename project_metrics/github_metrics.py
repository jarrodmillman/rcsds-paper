""" Calculate github metrics for projects

Data read from JSON file, abstracted via the Github API.

See fetch_project_data.py.
"""

import json
import datetime
from collections import OrderedDict

import pytz
import pandas as pd

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
    m['No of commits'] = len(valid_commits(repo['commits']))
    issues, prs = get_issues_prs(repo)
    issue_comments = valid(sum(get_comments(issues), []))
    pr_comments = valid(sum(get_comments(prs), []))
    m['No of issues'] = len(valid(issues))
    m['No of issue comments'] = len(issue_comments)
    m['Mean issue comment wc'] = mean_wc(issue_comments)
    m['No of PRs'] = len(valid(prs))
    m['No of PR comments'] = len(pr_comments)
    m['Mean PR comment wc'] = mean_wc(pr_comments)
    return m


def metrics_df(repos):
    dicts = [get_metrics(repo) for repo in repos.values()]
    names = [name.split('-')[1].capitalize() for name in repos]
    return pd.DataFrame(dicts, index=names)
