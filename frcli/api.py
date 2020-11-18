from frcli import constant
from frcli import util
import urllib.parse
import json

class FreshreleaseAPI(object):

	def __init__(self, domain, api_key):
		self.domain = domain
		self.api_key = api_key
		self.headers = {"Content-Type": "application/json", "Authorization": "Token " + self.api_key}

	def current_user(self):
		return util.get_request(constant.API_ENDPOINT.CURRENT_USER.url(self.domain), None, self.headers)

	def find_user(self,project, user=''):
		return util.get_request(constant.API_ENDPOINT.FIND_USER.url(self.domain, project, urllib.parse.quote(str(user))),None, self.headers)

	def find_all_users(self, project):
		 return util.get_request(constant.API_ENDPOINT.PROJECT_USERS.url(self.domain, project), None, self.headers)

	def find_all_subprojects(self, project):
		return util.get_request(constant.API_ENDPOINT.PROJECT_SQUADS.url(self.domain, project), None, self.headers)

	def find_all_issue_types(self, project):
		return util.get_request(constant.API_ENDPOINT.PROJECT_ISSUE_TYPES.url(self.domain, project), None, self.headers)

	def find_all_statuses(self, project):
		return util.get_request(constant.API_ENDPOINT.PROJECT_STATUS.url(self.domain, project), None, self.headers)

	def find_all_priorities(self, project):
		return util.get_request(constant.API_ENDPOINT.PROJECT_PRIORITIES.url(self.domain, project), None, self.headers)

	def filter_issues(self, project, query, page, size):
		return util.get_request(constant.API_ENDPOINT.FILTER_ISSUES.url(self.domain, project, query, page, size), None, self.headers)

	def find_issue_type_id_by_name(self, project, issue_type_name):
		response = json.loads(self.find_all_issue_types(project))
		
		if "issue_types" in response:
			issue_types = response["issue_types"]
			fn = filter(lambda issue_type: issue_type["name"].lower() == issue_type_name.lower(), issue_types)
			rs = list(fn)
			
			return rs[0]["id"] if len(rs) > 0 else None
		
		return None
		

	def find_status_id_by_name(self, project, status_name):
		response = json.loads(self.find_all_statuses(project))

		if "statuses" in response:
			statuses = response["statuses"]
			fn = filter(lambda status: status["name"].lower() == status_name.lower(), statuses)
			rs = list(fn)
			
			return rs[0]["id"] if len(rs) > 0 else None

		return None

	def find_priority_id_by_name(self, project, priority_name):
		response = json.loads(self.find_all_priorities(project))

		if "priorities" in response:
			priorities = response["priorities"]
			fn  = filter(lambda priority: priority["name"].lower() == priority_name.lower(), priorities)
			rs = list(fn)
			
			return rs[0]["id"] if len(rs) > 0 else None
		return None

	def find_subproject_id_by_name(self, project, sub_project_name):
		response = json.loads(self.find_all_subprojects(project))
		
		if "sub_projects" in response:
			sub_projects = response["sub_projects"]
			fn = filter(lambda sub_project: sub_project["name"].lower() == sub_project_name.lower(), sub_projects)
			rs = list(fn)
		
			return rs[0]["id"] if len(rs) > 0 else None
		return None

	def find_issue_by_id(self, project, issue_id):
		return util.get_request(constant.API_ENDPOINT.FIND_ISSUE.url(self.domain, project, issue_id), None, self.headers)

	def search_issues(self, project, search):
		return util.get_request(constant.API_ENDPOINT.SEARCH_ISSUES.url(self.domain, project, search), None, self.headers)

	def create_issue(self, project, issue_json):
		return util.post_request(constant.API_ENDPOINT.CREATE_ISSUE.url(self.domain, project), issue_json, self.headers)

	def update_issue(self, project, issue_id, issue_json):
		return util.put_request(constant.API_ENDPOINT.UPDATE_ISSUE.url(self.domain, project, issue_id), issue_json, self.headers)
