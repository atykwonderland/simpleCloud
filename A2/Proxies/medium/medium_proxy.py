import docker
from flask import Flask, jsonify, request
import os
import sys
import time

app = Flask(__name__)

client = docker.from_env()

MAX_MEDIUM_NODES = 15

nodes = []
jobs = []
job_queue = []
    
# node is container in docker
class Node:
    # list of dictionaires for output log
    # {'job_id': id, 'output': output}

    def __init__(self, name, id) -> None:
        self.jobs_output = []
        self.name = name
        self.status = "Idle"
        self.id = id

class Job:
    node_id = ""

    def __init__(self, file, status) -> None:
        self.file = file
        self.id = id(self.file)
        self.status = status

# this file contains all possible api calls that need docker commands 
# includes: resource manager and resource monitor api calls

#------------------------TOOLSET-------------------------

@app.route('/cloudproxy/init')
def cloud_init():
    print('Request to initialize medium pod')
    id = -1
    try:
        # if medium pod doesn't already exist
        pod = client.networks.get('medium_pod')
        result = str(pod.name) + ' was already created.'
        id = pod.id
    except docker.errors.NotFound:
        # create medium pod
        pod = client.networks.create('medium_pod', driver='bridge')
        result = str(pod.name) + ' was newly created.'
        id = pod.id
    
    # set node limit
    MAX_MEDIUM_NODES = 15

    # check if everything is ready for job
    filepaths = [f.path for f in os.scandir('.') if f.is_file()]
    dirpaths  = [f.path for f in os.scandir('.') if f.is_dir()]
    fp_error = False
    if './Dockerfile' in filepaths:
        if './medium_app' in dirpaths:
            app_filepaths = [f.path for f in os.scandir('./medium_app') if f.is_file()]
            if ('./app.py' not in app_filepaths) or ('./requirements.txt' not in app_filepaths):
                fp_error = True
        else:
            fp_error = True
    else:
        fp_error = True
    
    if fp_error:
        return jsonify({'response':'failure',
                        'reason': 'job directories/files missing/incorrect'})
    
    return jsonify({'response': 'success',
                    'result': result,
                    'id': id,
                    'name': 'medium_pod'})

#------------------------TOOLSET-------------------------

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6000)