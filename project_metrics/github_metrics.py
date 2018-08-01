""" Calculate github metrics for projects
"""

import datetime

import pytz
import github3

# Constants
ORG_NAME = 'berkeley-stat159'
INSTRUCTOR_LOGINS = ('rossbar', 'jarrodmillman', 'jbpoline', 'matthew-brett')
# See: https://registrar.berkeley.edu/sites/default/files/pdf/UCB_AcademicCalendar_2015-16.pdf
TERM_END = datetime.datetime(2015, 12, 18, 23, 59, 59, 999, pytz.utc)


def get_repos(*args):
    g = github3.GitHub(*args)
    org = g.organization(ORG_NAME)
    repos = list(org.repositories())
    return [r for r in repos if r.name.startswith('project-')]


def get_issues_prs(repo):
    issues_prs = list(repo.issues(state='all'))
    issues = [i for i in issues_prs if '/issues/' in i.html_url]
    prs = [i for i in issues_prs if '/pull/' in i.html_url]
    assert len(issues) + len(prs) == len(issues_prs)
    return issues, prs


def members_only(elements):
    return [e for e in elements if e.user.login not in INSTRUCTOR_LOGINS]


def in_term(elements):
    return [e for e in elements if e.created_at < TERM_END]


def valid(elements):
    return in_term(members_only(elements))


def get_comments(elements):
    return [list(e.comments()) for e in elements]


def word_count(text):
    for char in ',.:;\'"`-@()':
        text = text.replace(char, '')
    return len(text.split())


def mean_wc(elements):
    return sum(word_count(e.body) for e in elements) / len(elements)


def commit_dt(commit):
     dt_str = commit.as_dict()['commit']['author']['date']
     naive = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%XZ')
     return pytz.utc.localize(naive)


def get_metrics(repo):
    m = {}
    issues, prs = get_issues_prs(repo)
    m['issues'] = len(valid(issues))
    m['prs'] = len(valid(prs))
    issue_comments = valid(sum(get_comments(issues), []))
    pr_comments = valid(sum(get_comments(prs), []))
    m['issue_comments'] = len(issue_comments)
    m['issue_comment_mean_wc'] = mean_wc(issue_comments)
    m['pr_comments'] = len(pr_comments)
    m['pr_comment_mean_wc'] = mean_wc(pr_comments)
    return m
