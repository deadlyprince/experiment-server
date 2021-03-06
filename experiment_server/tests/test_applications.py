from experiment_server.models import (Application, Client, DataItem, Experiment, ExperimentGroup)
from experiment_server.views.applications import Applications
from .base_test import BaseTest
import datetime
import uuid

def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestApplications(BaseTest):
    def setUp(self):
        super(TestApplications, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_create_app(self):
        appsFromDB = Application.all()
        app1 = {
            'id': 1,
            'name': 'App 1'
        }
        app2 = {
            'id': 2,
            'name': 'App 2'
        }
        apps = [app1, app2]

        for i in range(len(appsFromDB)):
            for key in apps[i]:
                assert getattr(appsFromDB[i], key) == apps[i][key]

    def test_get_all_apps(self):
        appsFromDB = Application.all()
        assert len(appsFromDB) == 2

    def test_get_app(self):
        app1 = Application.get(1)
        app2 = Application.get(2)
        assert app1.id == 1 and app1.name == 'App 1'
        assert app2.id == 2 and app2.name == 'App 2'

    def test_save_app(self):
        app = Application(name='App 3')
        Application.save(app)
        appsFromDB = Application.all()
        assert len(appsFromDB) == 3

    def test_destroy_app(self):
        app1 = Application.get(1)
        Application.destroy(app1)
        appsFromDB = Application.all()
        app2 = Application.get(2)
        assert appsFromDB == [app2]
        assert len(appsFromDB) == 1

    def test_destroy_app_does_not_delete_dataitems(self):
        Application.save(Application(id=47, name='App to delete'))
        app = Application.get(47)
        Experiment.save(Experiment(id=78, application=app, name='Apperture'))
        exp = Experiment.get(78)
        ExperimentGroup.save(ExperimentGroup(id=67, name='GlaDos', experiment=exp))
        eg = ExperimentGroup.get(67)
        Client.save(Client(id=76, clientname='Chell', experimentgroups=[eg]))
        client = Client.get(76)
        DataItem.save(DataItem(key='key1',
               value=10,
               startDatetime=strToDatetime('2016-01-01 00:00:00'),
               endDatetime=strToDatetime('2016-01-01 01:01:01'),
               client=client))

        dataitem_count_before = DataItem.query().count()
        Application.destroy(app)
        dataitem_count_now = DataItem.query().count()

        assert dataitem_count_before == dataitem_count_now

    def test_get_confkeys_of_app(self):
        assert len(Application.get(1).configurationkeys) == 2
        ck = Application.get(1).configurationkeys[0]
        assert ck.name == 'highscore'

    def test_can_set_apikey(self):
        apikey = str(uuid.uuid4())
        app = Application(name='App with UUID', apikey=str(uuid.uuid4()))
        app = Application.save(app)

        expected = Application.get_by('apikey', apikey)

        assert expected == app

    def test_apikey_is_unique(self):
        apikey = str(uuid.uuid4())
        app = Application(name='App with UUID', apikey=str(apikey))
        app = Application.save(app)

        app = Application(name='Another app with UUID', apikey=str(apikey))
        was_added = True
        try:
            Application.save(app)
        except Exception as e:
            was_added = False
            pass

        assert not was_added

    def test_experimentdistribution_exists(self):
        experiment_distribution_exists = False

        app = Application(name='Banana')
        Application.save(app)
        app = Application.get_by('name', 'Banana')

        try:
            experiment_distribution = app.experiment_distribution
            experiment_distribution_exists = True
        except Exception as e:
            pass

        assert experiment_distribution_exists

    def test_experimentdistribution_can_be_set(self):
        app = Application(name='Banana', experiment_distribution='one_random')

        try:
            Application.save(app)
        except Exception as e:
            pass

        assert Application.get_by('name', 'Banana') is not None

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestApplicationsREST(BaseTest):
    def setUp(self):
        super(TestApplicationsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_applications_GET_one(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_GET_one()
        expected = Application.get(1).as_dict()
        assert response == expected

    def test_applications_GET_one_apikey_not_none(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_GET_one()
        assert response['apikey'] != None

    def test_applications_GET(self):
        httpApps = Applications(self.req)
        response = httpApps.applications_GET()
        expected = list(map(lambda _: _.as_dict(), Application.all()))
        assert response == expected

    def test_applications_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        response = httpApps.applications_DELETE_one()
        assert response.status_code == 400

    def test_applications_POST(self):
        self.req.swagger_data = {'application': Application(name='App 3')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()

        expected = Application.get_by('name', 'App 3').as_dict()
        assert response == expected

    def test_applications_POST_apikey_is_set(self):
        self.req.swagger_data = {'application': Application(name='App 3')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()

        expected = Application.get_by('name', 'App 3').as_dict()
        assert expected['apikey'] is not None

    def test_application_POST_name_is_not_empty(self):
        expected_count = Application.query().count()

        self.req.swagger_data = {'application': Application(name='')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()

        count_now = Application.query().count()
        assert expected_count == count_now

    def test_data_for_app_GET(self):
        from toolz import assoc, concat
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.data_for_app_GET()

        app = Application.get(1)
        configurationkeys = app.configurationkeys
        ranges = list(concat(list(map(lambda _: _.rangeconstraints, configurationkeys))))

        app_data = app.as_dict()
        app_data = assoc(app_data, 'configurationkeys', list(map(lambda _: _.as_dict(), configurationkeys)))
        app_data = assoc(app_data, 'rangeconstraints', list(map(lambda _: _.as_dict(), ranges)))
        app_data = assoc(app_data, 'exclusionconstraints', list(map(lambda _: _.as_dict(), httpApps.get_app_exclusionconstraints(1))))

        assert response == app_data

    def test_application_routes(self):
        assert self.req.route_url('application', id=1) == 'http://example.com/applications/1'
        assert self.req.route_url('applications') == 'http://example.com/applications'

    def test_applications_PUT_exists(self):
        app = Application.get(1)
        self.req.swagger_data = {'id': 1, 'application': app}
        httpApps = Applications(self.req)
        response = httpApps.applications_PUT()

        assert response == app.as_dict()

    def test_applications_PUT_ids_must_match(self):
        app = Application.get(1)
        self.req.swagger_data = {'id': 42, 'application': app}
        httpApps = Applications(self.req)
        response = httpApps.applications_PUT()

        assert response.status_code == 400

    def test_applications_PUT_application_must_exist(self):
        app = Application(id=42, name='Apperture Science')
        self.req.swagger_data = {'id': 42, 'application': app}
        httpApps = Applications(self.req)
        response = httpApps.applications_PUT()

        assert response.status_code == 400

    def test_applications_PUT(self):
        app = Application.get(1)
        expected_app_name = 'It is now changed'
        app.name = expected_app_name

        self.req.swagger_data = {'id': 1, 'application': app}
        httpApps = Applications(self.req)
        response = httpApps.applications_PUT()

        assert Application.get(1).name == expected_app_name

    def test_applications_PUT(self):
        expected_name = 'Veri specil'

        self.req.swagger_data = {'application': Application(name=expected_name)}
        httpApps = Applications(self.req)
        httpApps.applications_POST()

        app = Application.get_by('name', expected_name)
        apikey = app.apikey
        id = app.id
        self.req.swagger_data = {'id': app.id, 'application': Application(name='', apikey=apikey, id=id)}
        httpApps.applications_PUT()

        name_now = Application.get(id).name
        assert name_now == expected_name
