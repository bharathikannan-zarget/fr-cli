import os
from enum import Enum

HOME_DIR = os.environ['HOME']
CONFIG_LOCATION = HOME_DIR + "/.freshrelease"
CREDENTIALS_FILE = CONFIG_LOCATION + "/credentials"
CREDENTIALS_FILE_PERMISSION = 0o600

USER_FILE = CONFIG_LOCATION + "/user.json"
USER_FILE_PERMISSION = 0o600

STATUS_FILE = CONFIG_LOCATION + "/statuses.json"
STATUS_FILE_PERMISSION = 0o600

PRIORITY_FILE = CONFIG_LOCATION + "/priorities.json"
PRIORITY_FILE_PERMISSION = 0o600

SUBPROJECTS_FILE = CONFIG_LOCATION + "/subprojects.json"
SUBPROJECTS_FILE_PERMISSION = 0o600

VIEW_FILE = CONFIG_LOCATION + "/view.json"
VIEW_FILE_PERMISSION = 0o600

ISSUE_TYPES_FILE = CONFIG_LOCATION + "/issue_types.json"
ISSUE_TYPES_PERMISSION = 0o600

# CONFIG OPTIONS

API_KEY_PROMPT = "Freshrelease Api Key [{}]:"
DOMAIN_PROMPT = "Freshrelease Domain [{}]:"
DEFAULT_PROJECT_PROMPT = "Freshrelease Project Name [{}]:"


DEFAULT_HEADERS = ["key", "title", "squad", "owner", "status", "issue_type", "priority",  "created_at", "due_by"]

DEFAULT_SUBPROJECT_HEADERS = ["id", "name", "key", "type", "sprint_duration"]


## Issue Options

ISSUE_TITLE = "Title [{}]: "
ISSUE_DESCRIPTION = "Description [{}]: "
ISSUE_STATUS = "Status [{}]: "
ISSUE_PRIORITY = "Priority [{}]: "
ISSUE_SUBPROJECT = "Sub Project [{}]: "
ISSUE_OWNER = "Issue Owner [{}]: "
ISSUE_TYPE = "Issue Type [{}]: "


## Default Editor
DEFAULT_EDITOR = "vim"
EDITOR_MESSAGE = "Add your description here"

### API ENDPOINTS

class API_ENDPOINT(Enum):

	PROJECT_USERS = "https://{}/{}/users"
	PROJECT_SQUADS = "https://{}/{}/sub_projects"	
	PROJECT_STATUS = "https://{}/{}/statuses"
	PROJECT_ISSUE_TYPES = "https://{}/{}/issue_types"
	PROJECT_PRIORITIES = "https://{}/{}/priorities"
	PROJECT_ISSUES_BY_USER = "https://{}/{}/"
	FIND_USER = "https://{}/{}/users/suggest.json?q={}"
	FILTER_ISSUES = "https://{}/{}/issues?query_hash={}&sort=display_id&sort=desc&page={}&size={}&include=issue_type%2Cowner%2Cpriority%2Cstatus%2Csub_projects"
	FIND_ISSUE = "https://{}/{}/issues/{}?include=issue_type%2Cowner%2Cpriority%2Cstatus%2Csub_projects"
	SEARCH_ISSUES = "https://{}/{}/issues/suggest.json?q={}&include=issue_type%2Cowner%2Cpriority%2Cstatus%2Csub_projects"
	CURRENT_USER = "https://{}/sessions/current"
	CREATE_ISSUE = "https://{}/{}/issues"
	UPDATE_ISSUE = "https://{}/{}/issues/{}"

	def url(self, *argv):
		return self.value.format(*argv)

