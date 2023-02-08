from flask import Flask, jsonify, request
import docker
import time

app = Flask(__name__)
client = docker.from_env()

nodes = []
jobs = []

# pod is network in docker
class Pod:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id
    
# node is container in docker
class Node:
    # list of dictionaires for output log
    # {'job_id': id, 'output': output}
    jobs_output = []

    def __init__(self, name, id) -> None:
        self.name = name
        self.status = "Idle"
        self.id = id

class Job:
    def __init__(self, file, status, node_id) -> None:
        self.file = file
        self.id = id(self.file)
        self.status = status
        self.node_id = node_id

# this file contains all possible api calls that need docker commands 
# includes: resource manager and resource monitor api calls

#------------------------ALICE-------------------------

@app.route('/cloudproxy/init')
def cloud_init():
    try:
        # if default pod doesn't already exist
        pod = client.networks.get('default')
        result = str(pod.name) + ' was already created.'
    except docker.errors.NotFound:
        # create default pod
        pod = client.networks.create('default', driver='bridge')
        result = str(pod.name) + ' was newly created.'
    return jsonify({'result': result})

@app.route('/cloudproxy/pods/<name>', methods=['GET', 'DELETE'])
def cloud_pod(name):
    if request.method == 'GET':
        result = 'command unavailable due to lack of resources'
        return jsonify({'result': result})
    elif request.method == 'DELETE':
        # check if pod exists
        try:
            pod = client.networks.get(name)
            # check if pod is the default pod
            if name == 'default':
                result = str(name) + " cannot be removed. It is the default pod."
            # check if there are nodes registered to the pod
            elif len(pod.containers.list()) != 0:
                result = str(name) + " cannot be removed. There are nodes registered to this pod."
            # remove the pod
            else:
                pod.remove()
                result = str(name) + " has been removed successfully."
        except docker.errors.NotFound:
            # pod doesn't exist - can't delete
            result = str(name) + " not found"
        return jsonify({'result': result})

@app.route('/cloudproxy/nodes/<name>', defaults={'pod_name': 'default'}, methods=['GET'])
@app.route('/cloudproxy/nodes/<name>/<pod_name>', methods=['GET']) 
def cloud_node(name, pod_name):
    if request.method == 'GET':
        print('Request to register new node: ' + str(name) + ' in pod ' + str(pod_name))
        try:
            # check if pod exists
            pod = client.networks.get(pod_name)
            result = 'unknown'
            node_status = 'unknown'
            for node in nodes:
                # node already exists
                if name == node.name:
                    node_status = node.status
                    print('Node already exists: ' + str(name) + ' with status ' + str(node_status))
                    result = 'node already exists'
                    break
            # make new node
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image = "alpine", detach=True, network=pod.name)
                nodes.append(Node(name, n.id))
                result = 'node_added'
                node_status = 'IDLE'
                print('Successfully added a new node: ' + str(name))
            return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
        except docker.errors.NotFound:
            # pod doesn't exist - can't create node
            result = str(pod_name) + " not found"
            return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})
        
@app.route('/cloudproxy/nodes/<name>', methods=['DELETE'])   
def cloud_node_rm(name):
    if request.method == 'GET':
        try:
            # if node exists
            node_to_remove = client.containers.get(name)
            for i, node in nodes:
                if name == node.name:
                    # remove if status is idle
                    if node.status == 'IDLE':
                        node_to_remove.remove() 
                        result = 'successfully removed node: ' + str(name)
                        # remove the node from list of nodes as well
                        del nodes[i]
                        break
                    # reject if not idle
                    else:
                        result = 'node ' + str(name) + ' status is not IDLE'
                        break           
        except docker.errors.NotFound:
            # node doesn't exist - can't delete
            result = str(name) + " not found"
        return jsonify({'result': result})
    
@app.route('/cloud/jobs/launch', methods=['POST'])
def cloud_launch(file):
    # Create Job instance and print id
    job = Job(file, "Registered")
    jobs.append(job)
    print(job.id)
    # Look for available node
    while 1:
        for node in nodes:
            if node.status is "Idle":
                try:
                    container = client.containers.get(node.name)
                    # Set node & job status as "Running"
                    job.status = "Running"
                    node.status = "Running"
                    # Assgin job to the node
                    job.node_id = node.id
                    # Run the job
                    commands = file.readlines()
                    for command in commands:
                        (exec_code, output) = container.exec_run(command)
                        container.wait()
                        # Append logs to a file
                        file_name = str(job.id) + ".txt"
                        logs_file = open(file_name, "a")
                    # Save the log file to node
                    node.jobs_output.append({'job_output':job.id, 'output':logs_file})
                    # Update status when done running
                    job.status = "Completed"
                    node.status = "Idle"
                    result = 'Job ' + str(job.id) + ' is completed'
                    return jsonify({'result': result})
                except docker.errors.NotFound:
                    continue
    
@app.route('/cloud/job/abort/<job_id>', methods=['DELETE'])    
def cloud_abort(job_id):
    for job in jobs:
        if job.id is job_id:
            # Job registered, remove job from queue
            if job.status is "Registered":
                jobs.remove(job)
                result = 'Job ' + str(job_id) + ' is aborted'
                return jsonify({'result': result})
            # Job completed
            elif job.status is "Completed":
                result = 'Job ' +str(job_id) + " cannot be aborted. It has been completed."
                return jsonify({'result': result})
            # Job running
            elif job.status is "Running":
                for node in nodes:
                    if node.id is job.node_id:
                        try:
                            container = client.containers.get(node.name)
                            container.stop()
                            node.status = "Idle"
                            job.status = "Aborted"
                            result = 'Job ' + str(job_id) + 'is aborted'
                            return jsonify({'result': result})
                        except docker.errors.NotFound:
                            result = 'Container ' + str(node.name) + ' for job ' + str(job_id) + ' not found'
                            return jsonify({'result': result})
                result = 'Node ' + str(job.node_id) + ' for job' + str(job_id) + ' not found'
                return jsonify({'result': result})
    # Job not found in the queue
    result = 'Job ' + str(job_id) + " not found."
    return jsonify({'result': result})

#-------------------------------------------------

@app.route('/cloudproxy/nodes/all')
def cloud_get_all_nodes():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)