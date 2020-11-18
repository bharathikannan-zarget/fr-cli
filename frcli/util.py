import http.client, urllib.parse
from urllib.parse import urlparse
import json
import tempfile
import os
from subprocess import call
from frcli import constant
from tabulate import tabulate

class ApiError(Exception):

	def __init__(self, url, response_code, response):
			self.url = url
			self.response_code = response_code
			self.response = response
			self.message = "Operation Failed : {} with status code : {}, response received: {}".format(self.url, self.response_code, self.response or "")
			super().__init__(self.message)


def get_request(url, params={}, headers={}):
	result = urlparse(url)
	conn = None
	
	if result.scheme == 'https':
		conn = http.client.HTTPSConnection(result.netloc, 443)
	else:
		conn = http.client.HTTPConnection(result.netloc, 80)

	if params is not None:
		params = urllib.parse.urlencode(params)	
	path = result.path or ''
	query = result.query or ''
	conn.request("GET", path + '?' + query, params, headers)
	response = conn.getresponse()
	
	if response.status / 100 > 2:
		raise ApiError(url, response.status, response.read())

	return response.read()

def post_request(url, body='', headers={}):
	return make_request(url, "POST", body, headers)

def put_request(url, body='', headers={}):
	return make_request(url, "PUT", body, headers)

def make_request(url, method, body, headers={}):
	result = urlparse(url)
	conn = None

	if result.scheme == 'https':
		conn = http.client.HTTPSConnection(result.netloc, 443)
	else:
		conn = http.client.HTTPConnection(result.netloc, 80)
	
	path = result.path or ''
	query = result.query or ''
	conn.request(method, path + "?" + query, body, headers)
	response = conn.getresponse()

	if response.status / 100 > 2:
		raise ApiError(url, response.status, response.read())

	return response.read()
	

def print_response(data, view="json", collection_key=None, col_list=None, col_label=None):
	if data is None or len(data) == 0:
		print("")
		return
	json_response = json.loads(data)

	if view == "table" and collection_key is not None and collection_key in json_response:
		if type(json_response[collection_key] is dict):
			printTable([json_response[collection_key]], col_list, col_label)
		elif type(json_response[collection_key]) is list:
			printTable(json_response[collection_key], col_list, col_label)
		else:
			print(json_response[collection_key])
	else:
		print(json.dumps(json_response, indent=2))

def create_frelease_filter_query(conditions):
	if len(conditions) == 0:
		return ""
	query= []
	for condition in conditions:
		query.append({"condition": condition["q"], "operator" :"is_in", "value": str(condition["v"])})
	return urllib.parse.quote(json.dumps(query))

def open_editor(message):

	with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
		tf.write(bytes(message, "utf-8"))
		tf.flush()
		call([constant.DEFAULT_EDITOR, tf.name])
	
	with open(tf.name, 'r') as tf:
		edited_message = tf.read()
	return edited_message

		
def printTable(dataset, cols=None):
  	if cols is None:
  		header = dataset[0].keys()
  		rows =  [x.values() for x in dataset]
  	else:
  		header = cols
  		rows = []

  		for x in dataset:
  			row = []
  			for c in cols:
  				row.append(x.get(c, ""))
  			rows.append(row)

  	print(tabulate(rows, header, tablefmt="grid"))
