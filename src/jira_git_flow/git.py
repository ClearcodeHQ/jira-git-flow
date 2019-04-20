"""Git related functionality."""
import click
from subprocess import check_output


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
