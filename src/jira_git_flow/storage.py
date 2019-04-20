import click
import json
from marshmallow import Schema, fields, post_load
import os

from jira_git_flow import config
from jira_git_flow.models import JiraIssue


class Keys(object):
    current_story = 'current_story'
    current_issue = 'current_issue'
    stories = 'stories'


INIT_DATA = {
    Keys.current_story: None,
    Keys.current_issue: None,
    Keys.stories: [],
}


class IssueSchema(Schema):
    key = fields.Str()
    summary = fields.Str()
    status = fields.Str()
    type = fields.Str()

    @post_load
    def make_issue(self, data):
        return JiraIssue(**data)


class StorySchema(IssueSchema):
    subtasks = fields.Nested(IssueSchema, many=True)


class StorageSchema(Schema):
    current_story = fields.Nested(StorySchema, allow_none=True, exclude=["subtasks"])
    current_issue = fields.Nested(IssueSchema, allow_none=True)
    stories = fields.Nested(StorySchema, many=True, allow_none=True)


class Storage(object):
    """Storage based on JSON file."""
    def __init__(self, file, schema):
        self.file = file
        self.schema = schema
        self._init_data()
        self._load_data()

    def _load_data(self):
        try:
            with open(self.file, 'r') as f:
                file_data = json.load(f)
                schema_data = self.schema.load(file_data)
                if schema_data.errors:
                    exit('Failed to load data: {}'.format(schema_data.errors))
                self.data = self.schema.load(file_data).data
        except Exception:
            click.echo('Failed to load data. Starting with empty one.')
            self.data = INIT_DATA

    def _save_data(self):
        with open(self.file, 'w') as f:
            try:
                json_data = self.schema.dump(self.data).data
                json.dump(json_data, f, indent=4)
            except Exception as e:
                exit('Failed to save data: {}'.format(e))

    def _init_data(self):
        if not os.path.exists(self.file):
            with open(self.file, 'w+') as f:
                json.dump(INIT_DATA, f, indent=4)

    def get_current_story(self):
        """Return story currently work on."""
        return self._get_value(Keys.current_story)

    def get_current_issue(self):
        """Return issue currently work on."""
        return self._get_value(Keys.current_issue)

    def get_stories(self):
        """Return stories currently work on."""
        return self._get_value(Keys.stories)

    def get(self, type):
        return self._get_value(type)

    def update_issue(self, issue):
        stories = self.get_stories()
        try:
            story_index = stories.index(issue)
            stories[story_index] = issue
            self._save_data()
            return issue
        except ValueError:
            pass

        return self.update_subtask(issue)

    def update_subtask(self, subtask):
        stories = self.get_stories()
        for story in stories:
            try:
                subtask_index = story.subtasks.index(subtask)
                story.subtasks[subtask_index] = subtask
                self._save_data()
                return subtask
            except ValueError:
                pass

    def sync(self, stories):
        synced_stories = [JiraIssue.from_issue(story) for story in stories]
        self.data[Keys.stories] = synced_stories
        self._save_data()

    def resolve_issue(self, issue):
        self.data[Keys.current_issue] = None
        self._save_data()

    def add_issue(self, issue):
        if issue.type == 'story':
            self._add_unique(issue, Keys.stories)
            self.work_on_story(issue)
        else:
            parent = self._get_parent(issue)
            self._add_subtask(parent, issue)
            self.work_on_issue(issue)
        self._save_data()

    def work_on_story(self, story):
        """Keep state of current story."""
        self.data[Keys.current_story] = story
        self.data[Keys.current_issue] = None
        self._save_data()

    def work_on_issue(self, issue):
        """Keep state of current issue."""
        parent = self._get_parent(issue)
        self.work_on_story(parent)
        self.data[Keys.current_issue] = issue
        self._save_data()

    def finish(self, story):
        self.data[Keys.stories].remove(story)
        self.data[Keys.current_story] = None
        self._save_data()

    def _get_parent(self, issue):
        for story in self.data[Keys.stories]:
            if issue in story.subtasks:
                return story
        return self.get_current_story()

    def _add_subtask(self, story, subtask):
        stories = self.data[Keys.stories]
        stories[stories.index(story)].add_subtask(subtask)

    def _add_unique(self, issue, collection):
        if not any(i.key == issue.key for i in self.data[collection]):
            self.data[collection].append(issue)

    def _get_value(self, key):
        if key in self.data:
            return self.data[key]
        return None


storage_schema = StorageSchema()
storage = Storage(config.DATA_FILE, storage_schema)
