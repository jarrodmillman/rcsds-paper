""" Get repository data for projects, write as JSON

Usage:

    python fetch_project_data.py my-username my-password
"""
import sys
import json

import github3

# Constants
ORG_NAME = 'berkeley-stat159'


def get_repos(*args):
    g = github3.GitHub(*args)
    org = g.organization(ORG_NAME)
    repos = list(org.repositories())
    return [r for r in repos if
            (r.name.startswith('project-')
            and not r.name == 'project-template')]


def to_dicts(repo):
    repo_d = repo.as_dict()
    repo_d['issues'] = []
    for issue in repo.issues(state='all'):
        i_d = issue.as_dict()
        i_d['comment_contents'] = []
        for comment in issue.comments():
            i_d['comment_contents'].append(comment.as_dict())
        repo_d['issues'].append(i_d)
    repo_d['commits'] = [c.as_dict() for c in repo.commits()]
    return repo_d


def save_json(repos, fname):
    repos_d = {}
    for repo in repos:
        repos_d[repo.name] = to_dicts(repo)
    with open(fname, 'wt') as fobj:
        json.dump(repos, fobj)


def main():
    repos = get_repos(sys.argv[1:])
    save_json(repos, 'project_data.json')


if __name__ == '__main__':
    main()
