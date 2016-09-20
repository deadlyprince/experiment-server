from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils

from models.users import User


@view_defaults(renderer='json')
class Users(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='configurations', request_method="OPTIONS")
    def configurations_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        res.headers.add('Access-Control-Allow-Headers', 'username')
        return res

    # List configurations for specific user
    @view_config(route_name='configurations', request_method="GET")
    def configurations_GET(self):
        # Also adds the user to the DB if doesn't exist
        username = self.request.headers.get('username')
        user = self.DB.get_user(username)
        if user is None:
            print_log(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific user', None)
            return self.createResponse(None, 400)
        self.DB.assign_user_to_experiments(user.id)
        confs = self.DB.get_total_configuration_for_user(user.id)
        configurations = []
        for conf in confs:
            configurations.append({'key': conf.key, 'value': conf.value})
        result = {'data': configurations}
        print_log(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific user', result)
        return self.createResponse(result, 200)

    @view_config(route_name='users', request_method="OPTIONS")
    def users_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

    # List all users
    @view_config(route_name='users', request_method="GET", renderer='json')
    def users_GET(self):
        return User.all()

    @view_config(route_name='experiments_for_user', request_method="OPTIONS")
    def experiments_for_user_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

    # List all experiments for specific user
    @view_config(route_name='experiments_for_user', request_method="GET")
    def experiments_for_user_GET(self):
        id = int(self.request.matchdict['id'])
        experiments = self.DB.get_user_experiments_list(id)
        experimentsJSON = []
        for i in range(len(experiments)):
            expgroup = self.DB.get_experimentgroup_for_user_in_experiment(id, experiments[i].id)
            exp = experiments[i].as_dict()
            exp['experimentgroup'] = expgroup.as_dict()
            experimentsJSON.append(exp)
        result = {'data': experimentsJSON}
        print_log(datetime.datetime.now(), 'GET', '/users/' + str(id) + '/experiments',
                 'List all experiments for specific user', result)
        return self.createResponse(result, 200)

    @view_config(route_name='events', request_method="OPTIONS")
    def events_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        res.headers.add('Access-Control-Allow-Headers', 'username')
        return res

    # Save experiment data
    @view_config(route_name='events', request_method="POST")
    def events_POST(self):
        json = self.request.json_body
        value = json['value']
        key = json['key']
        startDatetime = json['startDatetime']
        endDatetime = json['endDatetime']
        username = self.request.headers['username']
        user = self.DB.get_user_by_username(username)
        if user is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', None)
            return self.createResponse(None, 400)
        result = {'data': self.DB.create_dataitem(
            {'user': user,
             'value': value,
             'key': key,
             'startDatetime': startDatetime,
             'endDatetime': endDatetime
             }).as_dict()}
        print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', result)
        return self.createResponse(result, 200)

    @view_config(route_name='user', request_method="OPTIONS")
    def user_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
        return res

    # Delete user
    @view_config(route_name='user', request_method="DELETE")
    def user_DELETE(self):
        id = int(self.request.matchdict['id'])
        result = self.DB.delete_user(id)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Failed')
            return self.createResponse(None, 400)
        print_log(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Succeeded')
        return self.createResponse(None, 200)
