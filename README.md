# jira-git-flow

The `jira-git-flow` is simple CLI tool to manage Jira flow along with
the git repository.

It allows to manage Jira stories and subtasks in simple way.
When new task is created the git branch with suitable name will be created
in local repository.

Tasks workflow (open -> progress -> review -> done) is managed with cli
commands.

## Usage

Available commands:

````
    git-flow --help
    Usage: git-flow [OPTIONS] COMMAND [ARGS]...

    Git flow.

    Options:
    --help  Show this message and exit.

    Commands:
    bug      Create (work on) bugfix.
    commit   Commit for issue
    feature  Create (work on) feature.
    finish   Finish story
    publish  Push branch to origin
    resolve  Resolve issue
    review   Move issue to review
    start    Start story/task
    status   Get work status
    story    Create a story
    sync     Sync stories between Jira and local storage
    workon   Work on story/issue.
````

### status

Get current work status.

### workon

Start working on specific story / task.

#### Chosing from local tasks

When command is run without any parameters task will be chosen from local
storage.

#### Search Jira for stories

Stories can be searched in Jira by adding keywords to command.
To get story by issue key use `-k` flag.

### story

Create new story and start working on it.

### feature / bug

Add subtask to current story and start working on it.
Subtask status will be set to `in_progess`. Git branch with suitable
name will be created on local repo.

### start / review / resolve

Change issue's status.

### commit

Make an git commit. Issue key will be added to the beginning of commit message.

### publish

Publish local branch on remote repository.

### sync

Sync local stories will remote Jira state.

## Configuration

Tool can be configured via two configuration files:

* credentials.json
* config.json

Both configuration files are located in `~/.config/jira-git-flow`.

Jira credentials must be set in `credentials.json`.

Configuration is done via `config.json` file. At the first run default
configuration file is created.

### url

Specifies base url to Jira instance.

### project

Specifies proejct key in Jira.

### statuses

There are following statuses used internally in `jira-git-flow`:

* open
* in_progress
* in_review
* done

Statuses configuration must be set to properly map
Jira statuses to internal ones.

Multiple Jira statues can be mapped to one internal status.

### actions

Action section defines tasks workflow.
There are following available actions:

* start_progress
* review
* resolve

Each action must define following attributes:

* `current_state` - task state for which action can be applied
* `transitions` - jira transitions applied to task when action will be performed
* `next_state` - task state set after action appliance

There is also optional `assign_to_user`. It specifies if issue should be assign to user on specific action.

Default actions are defined in `default` dictionary.

When specific issue type has it's own actions it can be specified in object
under issue type keyword.

### types
There are following internal issue types in `jira-git-flow`:

* story
* feature
* bug

Types section allows to define mapping between internal and Jira issue types.

Each type can have a prefix. Prefix will be added to git branch name.

### badges

Each status has a bagde to display in terminal.
Badges along with their colors can be defined in that section.
