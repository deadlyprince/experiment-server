from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface

@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		data = self.request.json_body
		name = data["name"]
		experimentgroups = data["experimentgroups"]
		self.DB.createExperiment({'name': name, 'experimentgroupNames': experimentgroups})

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET", renderer='../templates/all_experiments.jinja2')
	def experiments_GET(self):
		return {'experiments':self.DB.getAllExperiments()}

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET", renderer='../templates/experiment_metadata.jinja2')
	def experiment_metadata_GET(self):
		experiment = self.DB.getExperiment(self.request.matchdict['id'])
		return {'name': experiment.name, 'id': experiment.id, 'experimentgroups': experiment.experimentgroups}

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		self.DB.deleteExperiment(self.request.matchdict['id'])

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET")
	def users_for_experiment_GET(self):
		return None

	#11 Show experiment data
	@view_config(route_name='experiment_data', request_method="GET")
	def experiment_data_GET(self):
		return None





"""
@view_defaults(renderer='json')
class Hello:
	def __init__(self, request):
		self.request = request
	@view_config(route_name='hello', request_method="GET")
	def hello_get(self):
		return dict(a=1, b=2)
	@view_config(route_name='hello', request_method="POST")
	def hello_post(self):
		json = self.request.json_body
		json["kukkuu"] = "hellurei"
		json["hedari"] = self.request.headers["hedari"]
		self.request.headers["foo"] = 3
		return json

"""
#curl -H "Content-Type: application/json" -X POST -d '{"name":"First experiment","experimentgroups":["group A", "group B"]}' http://0.0.0.0:6543/experiments

#curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123

#curl -H "Content-Type: application/json" -H "hedari: todella paha" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123