# Experiment-server

A simple REST API server for providing runtime configurations for applications and receiving usage-related event data.

###Getting Started
---------------

$VENV/bin/pip install -e .

$VENV/bin/initialize_Experiment-server_db development.ini

$VENV/bin/pserve development.ini

Run tests:

$VENV/bin/py.test experiment_server/tests.py -q

###Trying the REST API using `curl`

Creating a new experiment:

    $ curl -H "Content-Type: application/json" -X POST -d '{"name": "My First Experiment", "experimentgroups": [{"name":"Group A", "configurations":[{"key":"key A", "value":4}]}, {"name": "Group B", "configurations":[{"key":"key B", "value":5}]}]}' http://localhost:6543/experiments

Deleting an experiment:

    $ curl -H "Content-Type: application/json" -X DELETE -d '' http://localhost:6543/experiments/1

###Work flow

When starting a new task:
- pull latest master
- make a local branch 

    $ git branch -b [task name]

- after committed your changes push them 

    $ git push origin [task name]

- remember to delete the branch

    $ git branch -d [task name] && git push origin :[task name]

- make a pull request: https://help.github.com/articles/creating-a-pull-request/


