import json
import os

BASE_DIRECTORY = os.path.expanduser('~') + '/.config/jira-git-flow/'
CREDENTIAL_FILE = BASE_DIRECTORY + 'credentials.json'
CONFIG_FILE = BASE_DIRECTORY + 'config.json'
DATA_FILE = BASE_DIRECTORY + 'data.json'

credentials = {
    'username': 'jira_username',
    'email': 'jira_email',
    'token': 'jira_token'
}

config = {
    'url': 'https://jira_url',
    'project': 'jira_project_key',
    'statuses': {
        'open': [
            'Open'
        ],
        'in_progress': 'In Progress',
        'in_review': 'Review',
        'resolved': [
            'Resolved', 'Done'
        ]
    },
    'actions': {
        'default': {
            'start_progress': {
                'current_state': 'open',
                'transitions': ['Start progress'],
                'next_state': 'in_progress',
                'assign_to_user': True
            },
            'review': {
                'current_state': 'in_progress',
                'transitions': ['To review'],
                'next_state': 'in_review'
            },
            'resolve': {
                'current_state': 'in_review',
                'transitions': ['Resolve', 'Release'],
                'next_state': 'resolved'
            }
        },
        'story': {
            'start_progress': {
                'transitions': ['Start progress'],
            },
            'review': {
                'transitions': ['Submit to review'],
            }
        }
    },
    'badges': {
        'open': {
            'badge': '•',
            'color': 'white'
        },
        'in_progress': {
            'badge': '•••',
            'color': 'blue'
        },
        'in_review': {
            'badge': '?',
            'color': 'yellow'
        },
        'resolved': {
            'badge': '✔',
            'color': 'green'
        }
    },
    'types': {
        'story': {
            'name': 'Story',
            'prefix': ''
        },
        'feature': {
            'name': 'Feature Sub-task',
            'prefix': 'f/'
        },
        'bug': {
            'name': 'BugFix Sub-task',
            'prefix': 'b/'
        }
    },
    'create_pull_request': True
}

if not os.path.exists(BASE_DIRECTORY):
    os.makedirs(BASE_DIRECTORY)

if os.path.exists(CREDENTIAL_FILE):
    with open(CREDENTIAL_FILE, 'r') as f:
        credentials = json.load(f)
else:
    with open(CREDENTIAL_FILE, 'w+') as f:
        json.dump(credentials, f, indent=4)
        exit('No credentials available. Configure credentials by editing {}'.format(CREDENTIAL_FILE))

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    with open(CONFIG_FILE, 'w+') as f:
        json.dump(config, f, indent=4)
        exit('No configuration detected. Configure app by editing {}'.format(CONFIG_FILE))

URL = config['url']
PROJECT = config['project']
USERNAME = credentials['username']
EMAIL = credentials['email']
TOKEN = credentials['token']
ACTIONS = config['actions']
STATUSES = config['statuses']
BADGES = config['badges']
ISSUE_TYPES = config['types']
CREATE_PULL_REQUEST = config['create_pull_request']
MAX_RESULTS = 100
