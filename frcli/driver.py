import fire
from frcli import constant
from frcli import util
from frcli import api
import configparser
from os import path
import getpass
import os
import configparser
import re
import json
import urllib.parse
import sys
import textwrap
import traceback

def save_config(options):
	config = configparser.ConfigParser()

	for k in options:
		if options[k] and len(options[k].strip()) > 0 and options[k] != 'None':
			config['DEFAULT'][k] = options[k]

	with open(constant.CREDENTIALS_FILE, 'w+') as file:
		config.write(file)
	os.chmod(constant.CREDENTIALS_FILE, constant.CREDENTIALS_FILE_PERMISSION)

def save_to_file(file_path, permission, data):
	with open(file_path, 'w+') as file:
		file.write(data)
	os.chmod(file_path, permission)

def is_valid(val):
	return val is not None and len(str(val).strip()) > 0

def save_default_configs_in_cache(domain, api_key, project):
	fr_api = api.FreshreleaseAPI(domain, api_key)
	statuses = fr_api.find_all_statuses(project)

	print("Your wait will be worth it!!!. We are caching...")

	try:
		statuses_json = json.loads(statuses)
	except json.decoder.JSONDecodeError:
		print("Error in retrieving default configs")
		return
	
	if "statuses" in statuses_json:
		save_to_file(constant.STATUS_FILE, constant.STATUS_FILE_PERMISSION, json.dumps(statuses_json["statuses"]))

	priorities = fr_api.find_all_priorities(project)

	try:
		priorities_json = json.loads(priorities)
	except json.decoder.JSONDecodeError:
		print("Error in retrieving default configs")
		return

	if "priorities" in priorities_json:
		save_to_file(constant.PRIORITY_FILE, constant.PRIORITY_FILE_PERMISSION, json.dumps(priorities_json["priorities"]))

	sub_projects = fr_api.find_all_subprojects(project)

	try:
		sub_projects_json = json.loads(sub_projects)
	except json.decoder.JSONDecodeError:
		print("Error in retrieving default configs")
		return
	
	if "sub_projects" in sub_projects_json:
		save_to_file(constant.SUBPROJECTS_FILE, constant.SUBPROJECTS_FILE_PERMISSION, json.dumps(sub_projects_json["sub_projects"]))

	issue_types = fr_api.find_all_issue_types(project)

	try:
		issue_types_json = json.loads(issue_types)
	except json.decoder.JSONDecodeError:
		print("Error in retrieving default configs")
		return

	if "issue_types" in issue_types_json:
		save_to_file(constant.ISSUE_TYPES_FILE, constant.ISSUE_TYPES_PERMISSION, json.dumps(issue_types_json["issue_types"]))

def find_field_id_by_name(project, is_default_project, cache_file, value, fallback_fn):
	if not is_default_project:
		return fallback_fn(project, value)
	rs = lookup_from_cache_file(cache_file, "name", value)
	return rs if rs is not None else fallback_fn(project, value)
		
	

def get_config():
	config = configparser.ConfigParser()
	config['DEFAULT'] = {'api_key': 'None', 'domain': 'None', 'project': 'None', 'user': 'None'}
	config.read(constant.CREDENTIALS_FILE)
	return config

def current_user():
	if os.path.exists(constant.USER_FILE):
		with open(constant.USER_FILE, 'r') as f:
			return json.loads(f.read())
	return None

def mask_secret(value):
	if not value:
		return ""
	size = len(value)
	masked = re.sub(r'.', '*', value[0: size - 4])
	return masked + value[size-4: size]

def save_current_user(domain, api_key):
	fr_api = api.FreshreleaseAPI(domain, api_key)
	current_user = fr_api.current_user()
	try:
		current_user_json = json.loads(current_user)
	except json.decoder.JSONDecodeError:
		print("Please check your credentials") 
		return False
	
	if "user" not in current_user_json:
		print("Please check your credentials.")
		return False
	
	with open(constant.USER_FILE, 'w+') as f:
		f.write(json.dumps(current_user_json["user"]))
	os.chmod(constant.USER_FILE, constant.USER_FILE_PERMISSION)

	return True

def lookup_from_cache_file(cache_file, filter_key, filter_value):
	if  not os.path.exists(cache_file):
		return None

	with open(cache_file, 'r') as file:
		try:
			arr = json.loads(file.read())
		except json.decoder.JSONDecodeError:
			print("Oops! File not in json format : " + cache_file)
			return None
	
	fn = filter(lambda entry: entry[filter_key].lower() == filter_value.lower(), arr)
	rs = list(fn)
	return rs[0]["id"] if len(rs) > 0 else None

def read_file_as_json(file):
	if not os.path.exists(file):
		return None

	with open(file, 'r') as file:
		try:
			return json.loads(file.read())
		except:
			print("Error in reading file from cache..")
			return None

	return None

def dict_to_map(arr, name, value):
	if arr is None:
		return {}

	o = {}
	for x in arr:
		if name in x and value in x:
			o[x.get(name)] = x.get(value)
	return o

def wrap(string, width=50):
	if string is None:
		return ""
	return "\n".join(textwrap.wrap(string, width=width))

def transform_issue_response(response):
	response = json.loads(response)
	sub_projects = dict_to_map(response.get("sub_projects", None), "id", "name")
	owners = dict_to_map(response.get("users", None), "id", "name")
	issue_types = dict_to_map(response.get("issue_types", None), "id", "label")
	priorities = dict_to_map(response.get("priorities", None), "id", "label")
	statuses = dict_to_map(response.get("statuses", None), "id", "label")


	def change_fields(issue_json):
		if is_valid(issue_json.get("status_id")):
			issue_json["status"] = statuses.get(issue_json.get("status_id"),issue_json.get("status_id")) 
			del issue_json["status_id"]

		if is_valid(issue_json.get("owner_id")):
			issue_json["owner"] = owners.get(issue_json.get("owner_id"), issue_json.get("owner_id"))
			del issue_json["owner_id"]

		if is_valid(issue_json.get("priority_id")):
			issue_json["priority"] = priorities.get(issue_json.get("priority_id"),issue_json.get("priority_id")) 
			del issue_json["priority_id"]

		if is_valid(issue_json.get("issue_type_id")):
			issue_json["issue_type"] = issue_types.get(issue_json.get("issue_type_id"), issue_json.get("issue_type_id")) 
			del issue_json["issue_type_id"]

		if is_valid(issue_json.get("sub_project_id")):
			issue_json["squad"] = sub_projects.get(issue_json.get("sub_project_id"), issue_json.get("sub_project_id"))
			del issue_json["sub_project_id"]

		if "description" in issue_json and is_valid(issue_json["description"]):
			issue_json["description"] = wrap(issue_json["description"])

		if "title" in issue_json and is_valid(issue_json["title"]):
			issue_json["title"] = wrap(issue_json["title"])

	if "issue" in response:
		change_fields(response["issue"])
		return response["issue"]
	elif "issues" in response:
		for issue in response["issues"]:
			change_fields(issue)
		return response["issues"]

	return response

def displayResponse(response, view, headers=None):
	if view == "json":
		print(json.dumps(response, indent=2))
	else:
		util.printTable(response, headers)		

def assert_cond(boolean, msg):
	if not boolean:
		print(msg)
		sys.exit(1)

class Project(object):

	def __init__(self):
		self.config = get_config()
		self.domain = self.config['DEFAULT']['domain']
		self.api_key = self.config['DEFAULT']['api_key']
		self.fr_api = api.FreshreleaseAPI(self.domain, self.api_key)
	
	def users(self, project=None, view=""):
		"""
			Get all users in the project. 

			Keyword Arguments:
			
			--project -- Name of the project. 
		"""
		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_all_users(project))
			displayResponse(response["users"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))


	def sub_projects(self, project=None, view=""):
		"""
			Get all squads in the project
			
			Keyword Arguments:

			--project -- Name of the project
		"""
		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_all_subprojects(project))
			displayResponse(response["sub_projects"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))

	def issue_types(self, project=None, view=""):
		"""
			Get all project issue types.

			Keyword Arguments:

			--project -- Name of the project
		"""
		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_all_issue_types(project))
			displayResponse(response["issue_types"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e))
		
	
	def statuses(self, project=None, view=""):
		"""
			List all statuses in the project.

			Keyword Arguments:
			
			--project -- Name of the project
		"""	
		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_all_statuses(project))
			displayResponse(response["statuses"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))

	def priorities(self, project=None, view=""):
		"""
			List all priorities in the project.

			Keyword Arguments:

			--project  -- Name of the project
		"""
		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_all_priorities(project))
			displayResponse(response["priorities"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))

	
	def find_user(self, name, project=None, view=""):
		"""
			Get all users in the project

			Keyword Arguments:
			
			--project -- Name of the project
			--user -- Name of the user or user id
		"""

		project = project or self.config['DEFAULT']['project']
		try:
			response = json.loads(self.fr_api.find_user(project, name))
			displayResponse(response["users"], view)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))
		
		

class Issue(object):

	def __init__(self):
		self.config = get_config()
		self.domain = self.config['DEFAULT']['domain']
		self.api_key = self.config['DEFAULT']['api_key']
		self.default_project = self.config['DEFAULT']['project']
		self.fr_api = api.FreshreleaseAPI(self.domain, self.api_key)
		self.user = current_user()

	def filter(self, project=None, user=None, status=None, priority=None, subproject=None, page=1, view=""):
		"""
			Filter the issues based on the filter condition

			Keyword Arguments:

			--project -- Name of the project
			--user -- Name of the user
			--status -- Issue status (Open, Closed and ...)
			--priority -- Issue priority (High, Urgent and ...)
			--subproject -- Name of the subproject
			--page -- Page number (default 1)
			--size -- Total issue to be fetched (default 30)
			--view -- json | table
		"""
		project = project or self.config['DEFAULT']['project']
		is_default_project = project == self.default_project
		conditions = []
		if user is not None:
			rs = json.loads(self.fr_api.find_user(project, user))
			owner_id = None
			if "users" in rs:
				assert_cond(len(rs["users"]) > 0, "User not exists")
				owner_id = rs["users"][0]["id"]
			conditions.append({"q": "owner_id", "v": owner_id})

		if status is not None:
			status_id = find_field_id_by_name(project, is_default_project, constant.STATUS_FILE, status, self.fr_api.find_status_id_by_name)
			assert_cond(status_id is not None, "Status not exists")
			conditions.append({"q": "status_id", "v": status_id})
		
		if priority is not None:
			priority_id = find_field_id_by_name(project, is_default_project, constant.PRIORITY_FILE, priority, self.fr_api.find_priority_id_by_name)
			assert_cond(priority_id is not None, "Priority not exists")
			conditions.append({"q": "priority_id", "v": priority_id})

		if subproject is not None:
			sub_project_id = find_field_id_by_name(project, is_default_project, constant.SUBPROJECTS_FILE, subproject, self.fr_api.find_subproject_id_by_name)
			assert_cond(sub_project_id is not None, "SubProject not exists")
			conditions.append({"q": "sub_project_id", "v": sub_project_id})

		try:
			response  = transform_issue_response(self.fr_api.filter_issues(project, util.create_frelease_filter_query(conditions), page, 30))
			displayResponse(response, view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))


	def create(self, project=None, view=""):
		"""
			Create an issue

			Keyword Arguments:
			
			--project -- Name of the project
			--view -- json | table
		"""
		status_id = subproject_id = priority_id = owner_id = issue_type_id = None
		project = project or self.config['DEFAULT']['project']
		is_default_project = project == self.default_project
		default_owner = self.user["name"] if self.user is not None else "None"
		default_owner_id = self.user["id"] if self.user is not None else "None" 
		title = input(constant.ISSUE_TITLE.format("None"))
		issue_type = input(constant.ISSUE_TYPE.format("None"))
		status = input(constant.ISSUE_STATUS.format("None"))
		priority = input(constant.ISSUE_PRIORITY.format("None"))
		subproject = input(constant.ISSUE_SUBPROJECT.format("None"))
		owner = input(constant.ISSUE_OWNER.format(default_owner))
		issue = {}
	
		try:
			description  = util.open_editor(constant.EDITOR_MESSAGE) or ''
			description = description.strip()
		except:
			description = input(constant.ISSUE_DESCRIPTION.format("None"))

		assert_cond(is_valid(title) and is_valid(issue_type), "Title and Issue Type cannot be empty")

		if is_valid(status):
			status_id = find_field_id_by_name(project, is_default_project, constant.STATUS_FILE, status, self.fr_api.find_status_id_by_name)
			assert_cond(status_id is not None, "Status not exists")
			issue["status_id"] = status_id

		if is_valid(priority):
			priority_id = find_field_id_by_name(project, is_default_project, constant.PRIORITY_FILE, priority, self.fr_api.find_priority_id_by_name)
			assert_cond(priority_id is not None, "Priority not exists")
			issue["priority_id"] = priority_id

		if is_valid(subproject):
			sub_project_id = find_field_id_by_name(project, is_default_project, constant.SUBPROJECTS_FILE, subproject, self.fr_api.find_subproject_id_by_name)
			assert_cond(sub_project_id is not None, "SubProject not exists")
			issue["sub_project_id"] = sub_project_id

		if is_valid(owner) and owner.lower() != default_owner.lower():
			rs = json.loads(self.fr_api.find_user(project, owner))
			if "users" in rs:
				assert_cond(len(rs["users"]) > 0, "Owner with the name doesn't exists")
				owner_id = rs["users"][0]["id"]
		else:
			owner_id = default_owner_id

		issue_type_id = find_field_id_by_name(project, is_default_project, constant.ISSUE_TYPES_FILE, issue_type, self.fr_api.find_issue_type_id_by_name)
		issue["issue_type_id"] = issue_type_id
		issue["owner_id"] = owner_id
		issue["title"] = title
		issue["description"] = description
		try:
			response = transform_issue_response(self.fr_api.create_issue(project, json.dumps({"issue": issue})))
			displayResponse([response], view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))


	def update(self, issue_id, project=None, status=None, priority=None, description=None, sub_project=None, title=None, view=""):
		"""
			Update an issue
			
			Keyword Arguments:

			--project -- Name of the project
			--issue_id -- Issue Identifier
			--status -- Issue Status
			--priority -- Issue Priority
			--description -- Issue Description
			--sub_project -- Subproject to be assigned.
			--title -- Issue Title
		"""
		project = project or self.default_project
		is_default_project = project == self.default_project
		issue = {}

		if is_valid(status):
			status_id = find_field_id_by_name(project, is_default_project, constant.STATUS_FILE, status, self.fr_api.find_status_id_by_name)
			assert_cond(status_id is not None, "Status not exists")
			issue["status_id"] = status_id

		if is_valid(priority):
			priority_id = find_field_id_by_name(project, is_default_project, constant.PRIORITY_FILE, priority, self.fr_api.find_priority_id_by_name)
			assert_cond(priority_id is not None, "Priority not exists")
			issue["priority_id"] = priority_id

		if is_valid(subproject):
			sub_project_id = find_field_id_by_name(project, is_default_project, constant.SUBPROJECTS_FILE, subproject, self.fr_api.find_subproject_id_by_name)
			assert_cond(sub_project_id is not None, "SubProject not exists")
			issue["sub_project_id"] = sub_project_id

		if is_valid(description):
			issue["description"] = description

		if is_valid(title):
			issue["title"] = title

		try:
			response = transform_issue_response(self.fr_api.update_issue(project, issue_id, json.dumps({"issue": issue})))
			displayResponse([response], view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))
		
	def change_status(self, issue_id, status, project=None, view=""):
		"""
			Update issue status

			Keyword Arguments:

			--project -- Name of the project
			--issue_id -- Issue identifier
			--status -- Status to change

		"""
		project = project or self.default_project
		is_default_project = project == self.default_project

		if is_valid(status):
			status_id = find_field_id_by_name(project, is_default_project, constant.STATUS_FILE, status, self.fr_api.find_status_id_by_name)

		issue = {"status_id": status_id}
		try:
			response = transform_issue_response(self.fr_api.update_issue(project, issue_id, json.dumps({"issue": issue})))
			displayResponse([response], view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))


	def find(self, project=None, issue_id=None, view=""):
		"""
			Find an issue
			
			Keyword Arguments:

			--project -- Name of the project
			--issue_id -- Issue identifier
		"""
		project = project or self.config['DEFAULT']['project']
		is_default_project = project == self.default_project
		assert issue_id is not None, "Issue ID is mandatory"
		try:
			response = transform_issue_response(self.fr_api.find_issue_by_id(project, issue_id))
			displayResponse([response], view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))
	
	def search(self, project=None, query=None, view=""):
		"""
			Search issues
			
			Keyword Arguments:
	
			--project -- Name of the project
			--query -- Search string
		"""
		project = project or self.config['DEFAULT']['project']
		assert query is not None and len(query) > 3, "Query should be minimum 3 characters"
		try:
			response = transform_issue_response(self.fr_api.search_issues(project, query))
			displayResponse(response, view, constant.DEFAULT_HEADERS)
		except util.ApiError as e:
			print(str(e.message))
		except Exception as e:
			print(str(e.message))



class Pipeline(object):

	def __init__(self):
		self.project = Project()
		self.issue = Issue()

	def configure(self):
		"""
			Configure Freshrelease options
		"""
		if not path.exists(constant.CONFIG_LOCATION):
			os.mkdir(constant.CONFIG_LOCATION)

		#defaults
		existing_api_key = existing_project = existing_domain = masked_api_key = None

		if path.exists(constant.CREDENTIALS_FILE):
			config = configparser.ConfigParser()
			config['DEFAULT'] = {'api_key': 'None', 'domain': 'None', 'project': 'None', 'editor': "vim"}
			config.read(constant.CREDENTIALS_FILE)
			existing_api_key = config['DEFAULT']['api_key']
			masked_api_key = mask_secret(existing_api_key)
			existing_domain = config['DEFAULT']['domain']
			existing_project = config['DEFAULT']['project']
	
		api_key = getpass.getpass(prompt = constant.API_KEY_PROMPT.format(masked_api_key))
		domain = input(constant.DOMAIN_PROMPT.format(existing_domain))
		project = input(constant.DEFAULT_PROJECT_PROMPT.format(existing_project))
		domain = domain or existing_domain
		project = project or existing_project
		api_key = api_key or existing_api_key

		save_config({'api_key': api_key, 'domain': domain, 'project': project})
		if save_current_user(domain or existing_domain, api_key or existing_api_key):
			save_default_configs_in_cache(domain, api_key, project)
			print("Successfully verified credentials")
		else:
			print("Incorrect credentials, please check your domain or api key")

	def reload(self):
		"""
			Reload cached configurations
		"""
		config = get_config()
		domain = config['DEFAULT']['domain']
		api_key = config['DEFAULT']['api_key']
		project = config['DEFAULT']['project']

		if not save_current_user(domain, api_key):
			print("Invalid credentials, try to reconfigure using `configure` command")
		
		save_default_configs_in_cache(domain, api_key, project)
		print("Reloaded...")	
		

	def clear(self):
		"""
			Clears stored credentials.
		"""
		confirmation = input("Type `yes` to confirm:") or ""

		if confirmation.lower().strip() == "yes":
			for f in [constant.CREDENTIALS_FILE, constant.USER_FILE, constant.STATUS_FILE, constant.PRIORITY_FILE, constant.SUBPROJECTS_FILE]:
				if os.path.exists(f):
					os.remove(constant.CREDENTIALS_FILE)
			print("Cleared...")
		else:
			print("You opted out..")

def main():
	fire.Fire(Pipeline)
