"""Git related functionality."""
import re
import webbrowser
from urllib.parse import quote_plus

import click
from subprocess import check_output

REMOTE_URL_REGEXP = '(https://|git@)([^:/]*)(:|/)(.*)\\.git'

GIT_PROVIDERS = {
    'bitbucket.org': {
        'pull_request': '{project}/pull-requests/new?source={branch}&t=1'
    },
    'github.com': {
        'pull_request': '{project}/pull/new/{branch}'
    }
}


def checkout(branch):
    """Checkout branch"""
    click.echo('Checkout on branch {}...'.format(branch))
    if branch_exists(branch):
        check_output(['git', 'checkout', branch])
        return
    check_output(['git', 'checkout', '-b', branch])


def commit(message):
    """Commit."""
    check_output(['git', 'commit', '-a', '-m', '{}'.format(message)])


def push(branch, remote='origin'):
    """Push branch."""
    check_output(['git', 'push', '-u', remote, branch])


def branch_exists(branch_name):
    """Check if branch exists eiither local or remote"""
    branches = check_output(['git', 'branch', '-a']).decode('utf-8').split('\n')
    return bool([branch for branch in branches if branch_name in branch])


def remote_data(remote='origin'):
    """Get remote provider and project."""
    remote_url = check_output(
        ['git', 'remote', 'get-url', remote]
    ).strip().decode()

    match = re.match(REMOTE_URL_REGEXP, remote_url)
    if match:
        return match.group(2), match.group(4)
    raise ValueError('Could not get remote git data.')


def create_pull_request(branch):
    """Open pull request creation view in browser."""
    provider, project = remote_data()
    try:
        url = 'https://{provider}/{pull_request_url}'.format(
            provider=provider,
            pull_request_url=GIT_PROVIDERS[provider]['pull_request'].format(
                project=project,
                branch=quote_plus(branch)
            )
        )
        webbrowser.open(url)
    except KeyError:
        click.exit('Unable to create pull request')
