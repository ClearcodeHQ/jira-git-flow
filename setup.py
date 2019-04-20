#!/usr/bin/env python
"""Project setup."""
from setuptools import setup, find_packages

package_version = '0.0.1'

requirements = [
    'click==6.7',  # CLI interface framework
    'bumpversion==0.5.3',  # version number management
    'jira==2.0.0',  # JIRA client
    'wheel==0.29.0',  # adds support for building wheels
    'pbr>=3.0.0',  # jira dependency, https://github.com/pycontribs/jira/issues/501
    'marshmallow==2.16.3'
]

requirements_tests = [
    'bandit==1.4.0',
    'mock==2.0.0',
    'pytest==3.7.4',  # tests framework used
    'pylama==7.4.1',  # code linter
    'mccabe==0.6.1',
    'pytest-cov==2.5.1',
    'pylint==1.7.2',
    'pycodestyle==2.3.1',
    'pydocstyle==2.0.0',
]

setup(
    name='jira-git-flow',
    version=package_version,
    author='Bartosz Lichenski',
    description="Manage JIRA with git commands",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    tests_require=requirements_tests,
    extras_require={
        'tests': requirements_tests
    },
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'git-flow = jira_git_flow:git_flow',
        ],
    },
)
