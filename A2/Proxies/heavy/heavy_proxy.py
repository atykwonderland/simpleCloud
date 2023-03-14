import docker
from flask import Flask, jsonify, request
import os
import sys
import time

app = Flask(__name__)

client = docker.from_env()

MAX_HEAVY_NODES = 15

nodes = []
    
# node is container in docker
class Node:
    # list of dictionaires for output log
    # {'job_id': id, 'output': output}

    def __init__(self, name, id) -> None:
        self.jobs_output = []
        self.name = name
        self.status = "New"
        self.id = id

#------------------------TOOLSET-------------------------

@app.route('/cloudproxy/init')
def cloud_init():
    print('Request to initialize heavy pod')
    id = -1
    try:
        # if heavy pod doesn't already exist
        pod = client.networks.get('heavy_pod')
        result = str(pod.name) + ' was already created.'
        id = pod.id
    except docker.errors.NotFound:
        # create heavy pod
        pod = client.networks.create('heavy_pod', driver='bridge')
        result = str(pod.name) + ' was newly created.'
        id = pod.id
    
    # set node limit
    MAX_HEAVY_NODES = 15

    # check if everything is ready for job
    filepaths = [f.path for f in os.scandir('.') if f.is_file()]
    dirpaths  = [f.path for f in os.scandir('.') if f.is_dir()]
    fp_error = False
    if './Dockerfile' in filepaths:
        if './heavy_app' in dirpaths:
            app_filepaths = [f.path for f in os.scandir('./heavy_app') if f.is_file()]
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
                    'name': 'heavy_pod'})

#TODO: Hana
@app.route('/cloudproxy/nodes/<name>/<pod_name>', methods=['GET']) 
def cloud_node(name, pod_name):
    if request.method == 'GET':
        print('Request to register new node: ' + str(name) + ' in pod ' + str(pod_name))
        try:
            # check if pod exists
            pod = client.networks.get(pod_name)
            result = 'unknown'
            node_status = 'unknown'
            # check if the limit of the pod has been met
            if node.size() >= 10:
                print('Pod' + str(pod_name) + 'is already at its maximum resource capacity')
                result = 'pod at maximum reasource capacity'
                return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})
            for node in nodes:
                # node already exists
                if name == node.name:
                    node_status = node.status
                    print('Node already exists: ' + str(name) + ' with status ' + str(node_status))
                    result = 'node already exists'
                    return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
            # make new node
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image = "alpine", command='/bin/sh', detach=True, tty=True, name=str(name), network=pod.name)
                nodes.append(Node(name, n.id, pod_name))
                result = 'node_added'
                node_status = 'New'
                print('Successfully added a new node: ' + str(name) + 'to pod' + str(pod_name))
            return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
        except docker.errors.NotFound:
            # pod doesn't exist - can't create node
            result = str(pod_name) + " not found"
            return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})

#TODO: Hana
@app.route('/cloudproxy/nodes/<name>/<pod_name>', methods=['GET']) 
def cloud_node(name, pod_name):
    if request.method == 'GET':
        print('Request to register new node: ' + str(name) + ' in pod ' + str(pod_name))
        try:
            # check if pod exists
            pod = client.networks.get(pod_name)
            result = 'unknown'
            node_status = 'unknown'
            # check if the limit of the pod has been met
            if node.size() >= 10:
                print('Pod' + str(pod_name) + 'is already at its maximum resource capacity')
                result = 'pod at maximum reasource capacity'
                return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})
            for node in nodes:
                # node already exists
                if name == node.name:
                    node_status = node.status
                    print('Node already exists: ' + str(name) + ' with status ' + str(node_status))
                    result = 'node already exists'
                    return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
            # make new node
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image = "alpine", command='/bin/sh', detach=True, tty=True, name=str(name), network=pod.name)
                nodes.append(Node(name, n.id, pod_name))
                result = 'node_added'
                node_status = 'New'
                print('Successfully added a new node: ' + str(name) + 'to pod' + str(pod_name))
            return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
        except docker.errors.NotFound:
            # pod doesn't exist - can't create node
            result = str(pod_name) + " not found"
            return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})

#TODO: Joshua
@app.route('/cloudproxy/nodes/rm/<name>')   
def cloud_node_rm(name):
    print('Request to remove node: ' + str(name))
    try:
        # if node exists
        node_to_remove = client.containers.get(name)
        for i in range(len(nodes)):
            if name == nodes[i].name:
                # remove if status is idle
                if nodes[i].status == 'New':
                    node_to_remove.stop()
                    node_to_remove.remove() 
                    result = 'successfully removed node: ' + str(name)
                    # remove the node from list of nodes as well
                    del nodes[i]
                    return jsonify({'result': result})
                # reject if not idle
                else:
                    result = 'node ' + str(name) + ' status is not New'
                    return jsonify({'result': result})
        result = 'node ' + str(name) + ' was not instantiated for this cloud.'
        return jsonify({'result': result})
    except docker.errors.NotFound:
        # node doesn't exist - can't delete
        result = str(name) + ' not found'
        return jsonify({'result': result})

#------------------------TOOLSET-------------------------

#------------------------MONITORING-------------------------

#TODO: Joshua
@app.route('/cloudproxy/nodes/<pod_id>')
def cloud_node_ls(pod_id):
    result = []
    for node in nodes:
    # name, ID and status must be printed to stdout
    # currently only accomodates one resource pod -- need to change for future cluster
        n = {'node_name':node.name, 'node_id':node.id, 'status':node.status}
        result.append(n)
    return jsonify(result)

#------------------------MONITORING-------------------------

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6000)
