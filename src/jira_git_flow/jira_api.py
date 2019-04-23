import click
from jira import JIRA, JIRAError


class Jira(object):
    """JIRA objects and operations."""

    def __init__(self, url, username, token, project, max_results):
        self.jira = JIRA(url, basic_auth=(username, token))
        self.project = project
        self.max_results = max_results

    def search_issues(self, keyword, **kwargs):
        """
        Search Jira issues.

        Filtering by keyword is not done on JIRA query becasue it does not support
        filtering both summary and key by string values.
        """
        keyword = keyword.lower()
        query_parameters = []
        if kwargs.get('type'):
            query_parameters.append('type = "{}"'.format(kwargs.get('type')))

        query = ' OR'.join(query_parameters) + ' order by created desc'
        issues = self.jira.search_issues(query, maxResults=self.max_results)

        matching_issues = []
        for issue in issues:
            if keyword in issue.key.lower() or keyword in issue.fields.summary.lower():
                matching_issues.append(issue)

        return matching_issues

    def get_issue_by_key(self, key):
        """Get issue by key"""
        try:
            return self.jira.issue(key)
        except JIRAError as e:
            if e.status_code == 404:
                raise click.UsageError('The specified JIRA issue: {}, does not exist.'.format(key))
            raise

    def create_issue(self, fields):
        return self.jira.create_issue(fields=fields)

    def get_resolution_by_name(self, name):
        resolutions = self.jira.resolutions()
        for r in resolutions:
            if r.name == name:
                return r.id
        return None

    def get_transition(self, issue, name):
        return self.jira.find_transitionid_by_name(issue, name)

    def transition_issue(self, issue, transition):
        transition_id = self.get_transition(issue, transition)
        if transition_id:
            self.jira.transition_issue(issue, transition_id)

    def assign_issue(self, issue, assignee):
        self.jira.assign_issue(issue, assignee)
