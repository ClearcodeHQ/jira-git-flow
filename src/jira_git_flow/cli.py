"""Cli module"""
import click
from PyInquirer import style_from_dict, Token, prompt, Separator

from jira_git_flow import config
from jira_git_flow.models import JiraIssue
from jira_git_flow.storage import storage


ELEMENT_BRANCH = '├'
LAST_ELEMENT_BRANCH = '└'
PARENT_BRANCH = '│'
SPACES_PER_LEVEL = 2


def get_issue_fields(type, subtask):
    issue = {}
    if subtask:
        current_story = storage.get_current_story()
        click.echo('Creating subtask for story {}'.format(current_story))
        issue['parent'] = {
            'key': current_story.key
        }

    summary = click.prompt('Please enter {} summary'.format(type), type=str)
    click.echo('Please enter {} description:'.format(type))
    description = _get_multiline_input()
    fields = {
        'project': {'key': config.PROJECT},
        'summary': summary,
        'description': description,
        'issuetype': {
            'name': config.ISSUE_TYPES[type]['name'],
            'subtask': subtask
        },
    }

    issue.update(fields)

    return issue


def _get_multiline_input():
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return '\n'.join(lines)


def choose_issues_from_simple_view(issues):
    if not issues:
        exit('No issues.')
    click.echo('Matching issues')
    for idx, issue in enumerate(issues):
        issue_model = JiraIssue.from_issue(issue)
        click.echo('{}: {} {}'.format(idx, issue_model.key, issue_model.summary))
    issue_id = click.prompt('Choose issue', type=int)
    return issues[issue_id]


def choose_issue():
    return choose_from_story_tree(lambda issue: True)[0]


def choose_by_types(types):
    return choose_from_story_tree(lambda issue: issue.type in types)


def choose_by_status(status):
    return choose_from_story_tree(lambda issue: issue.status == status)


def choose_from_story_tree(filter_function):
    render_stories(filter_function)
    user_input = click.prompt('Choose issue(s)', type=str)
    return get_issues_from_input(user_input)


def get_issues_from_input(user_input):
    stories = storage.get_stories()
    issues = []
    try:
        for issue_id in user_input.replace(' ', '').split(','):
            if len(issue_id.split('.')) == 1:
                issue = stories[int(issue_id)]
            else:
                story, task = issue_id.split('.')
                issue = stories[int(story)].subtasks[int(task)]
            issues.append(issue)

        return issues
    except IndexError:
        exit('Incorrect issue number.')


def render_stories(filter_function=None):
    stories = storage.get_stories()
    level = 0

    for index, story in enumerate(stories):
        is_last_story = is_last(index, stories)
        render_item(story, index, level, is_last_story, False, filter_function)
        render_subtasks(story.subtasks, index, is_last_story, filter_function)


def render_subtasks(subtasks, story_id, last_story, filter_function=None):
    level = 1
    if not subtasks:
        render_space(level, last_story)

    for index, subtask in enumerate(subtasks):
        is_last_subtask = is_last(index, subtasks)
        item_id = '{}.{}'.format(story_id, index)
        render_item(subtask, item_id, level, is_last_subtask, last_story,
                    filter_function)
        if is_last_subtask:
            render_space(level, last_story)


def render_item(item, item_id, level, is_last, is_last_parent,
                filter_function=None):
    if filter_function and filter_function(item):
        item_id = '({})'.format(item_id)
    else:
        item_id = ''

    render_tree_line(item, level, is_last, is_last_parent, item_id)


def render_tree_line(item, level, last_item, last_parent, item_id):
    branch = get_tree_branch(level, last_item, last_parent)
    badge = render_badge(item)
    issue_key = render_issue_key(item)
    tree_line = '{}{}: {} {} {}'.format(branch, issue_key, item.summary,
                                        badge, item_id)
    click.echo(tree_line)


def render_space(level, last_parent):
    indent = get_indent(level, get_parent_branch(level, last_parent))
    click.echo(indent)


def get_tree_branch(level, last_item, last_parent):
    element_branch = get_element_branch(last_item)
    parent_branch = get_parent_branch(level, last_parent)
    indent = get_indent(level, parent_branch)

    return '{}{}─'.format(indent, element_branch)


def get_element_branch(last_item):
    if last_item:
        return LAST_ELEMENT_BRANCH
    return ELEMENT_BRANCH


def get_parent_branch(level, last_parent):
    if level > 0 and not last_parent:
        return PARENT_BRANCH
    return ''


def get_indent(level, parent_branch):
    indent = ' ' * SPACES_PER_LEVEL
    for _ in range(level):
        indent += parent_branch + ' ' * SPACES_PER_LEVEL
    return indent


def render_issue_key(issue):
    underline = False
    if storage.get_current_issue():
        if working_on_issue(issue):
            underline = True
    else:
        if working_on_story(issue):
            underline = True
    return click.style(issue.key, bold=True, underline=underline)


def render_badge(issue):
    badge = config.BADGES[issue.status]['badge']
    color = config.BADGES[issue.status]['color']
    return click.style(badge, fg=color)


def is_last(index, collection):
    return index == len(collection)-1


def working_on_issue(issue):
    current_issue = storage.get_current_issue()
    if current_issue:
        return issue == current_issue
    return False


def working_on_story(story):
    current_story = storage.get_current_story()
    if current_story:
        return story == current_story
    return False


# INTERACTIVE
def interactive_choose_by_status(status):
    return choose_interactive(lambda issue: issue.status == status)


def choose_interactive(filter_function=lambda issue: True):
    stories = storage.get_stories()

    style = style_from_dict({
        Token.Separator: '#6C6C6C',
        Token.QuestionMark: '#FF9D00 bold',
        # Token.Selected: '',  # default
        Token.Selected: '#5F819D',
        Token.Pointer: '#FF9D00 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#5F819D bold',
        Token.Question: '',
    })

    questions = [
        {
            'type': 'checkbox',
            'qmark': '?',
            'message': 'Choose issues',
            'name': 'issues',
            'choices': convert_stories_to_choices(stories, filter_function),
        }
    ]

    answers = prompt(questions, style=style)

    if not 'issues' in answers:
        return []

    return answers['issues']


def convert_stories_to_choices(stories, filter_function):
    choices = []
    for story in stories:
        choices.append(Separator(story.full_name))
        for subtask in story.subtasks:
            subtask_choice = {
                'name': subtask.full_name,
                'value': subtask
            }
            if not filter_function(subtask):
                subtask_choice['disabled'] = True
            choices.append(subtask_choice)

    if not has_active_choices(choices):
        exit("There are no tasks with selected filters.")

    return choices


def has_active_choices(choices):
    for choice in choices:
        if not isinstance(choice, Separator):
            if not 'disabled' in choice:
                return True
    return False

def get_pointer_index(stories):
    flatten_issues = get_flatten_issues(stories)
    current_issue = storage.get_current_issue()
    current_story = storage.get_current_story()

    for current in [current_issue, current_story]:
        if current:
            try:
                return flatten_issues.index(current)
            except ValueError:
                pass
    return 0


def get_flatten_issues(stories):
    flatten_issues = []
    for story in stories:
        flatten_issues.append(story)
        flatten_issues.extend(story.subtasks)
    return flatten_issues
