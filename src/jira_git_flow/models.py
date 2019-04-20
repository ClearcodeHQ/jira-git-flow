"""Local models"""
from jira_git_flow import config


class JiraIssue(object):
    """Jira simplified issue"""
    def __init__(self, key, summary, type, status, subtasks=[]):
        self.key = key
        self.summary = summary
        self.type = type
        self.status = status
        self.subtasks = subtasks

    def __hash__(self):
        return self.key.split('-')[1]

    def __eq__(self, obj):
        return self.key == obj.key

    def __repr__(self):
        return '{}: {}'.format(self.key, self.summary)

    @classmethod
    def from_issue(cls, issue):
        if isinstance(issue, cls):
            return issue
        return cls(issue.key, issue.fields.summary, _get_type(issue), _get_status(issue),
                   _get_subtasks(issue))

    def add_subtask(self, subtask):
        if subtask not in self.subtasks:
            self.subtasks.append(subtask)


def _get_subtasks(jira_issue):
    try:
        return [JiraIssue.from_issue(subtask) for subtask in jira_issue.fields.subtasks]
    except AttributeError:
        return []


def _get_type(jira_issue):
    jira_type = jira_issue.fields.issuetype.name
    for key, value in config.ISSUE_TYPES.items():
        if jira_type == value['name']:
            return key
    return None


def _get_status(jira_issue):
    jira_status = jira_issue.fields.status.name
    for key, value in config.STATUSES.items():
        if jira_status in value:
            return key
    return None
