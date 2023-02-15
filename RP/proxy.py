from flask import Flask, jsonify, request
import docker
import time

app = Flask(__name__)
client = docker.from_env()

nodes = []
jobs = []
job_queue = []

# pod is network in docker
# not used yet since no resource clusters
class Pod:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id
    
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
    print('Request to initialize cloud')
    try:
        # if default pod doesn't already exist
        pod = client.networks.get('default_pod')
        result = str(pod.name) + ' was already created.'
    except docker.errors.NotFound:
        # create default pod
        pod = client.networks.create('default_pod', driver='bridge')
        result = str(pod.name) + ' was newly created.'
    # TODO: setup and run dispatch function somehow
    return jsonify({'result': result})

@app.route('/cloudproxy/pods/<name>', methods=['GET'])
def cloud_pod(name):
    if request.method == 'GET':
        print('Request to register new pod: ' + str(name))
        result = 'command unavailable due to lack of resources'
        return jsonify({'result': result})

@app.route('/cloudproxy/pods/rm/<name>', methods=['GET'])
def cloud_pod_rm(name):
    if request.method == 'GET':
        print('Request to remove pod: ' + str(name))
        # check if pod exists
        try:
            pod = client.networks.get(name)
            # check if pod is the default pod
            if name == 'default_pod':
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

@app.route('/cloudproxy/nodes/<name>', defaults={'pod_name': 'default_pod'}, methods=['GET'])
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
                    return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
            # make new node
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image = "alpine", command='/bin/sh', detach=True, tty=True, name=str(name), network=pod.name)
                nodes.append(Node(name, n.id))
                result = 'node_added'
                node_status = 'Idle'
                print('Successfully added a new node: ' + str(name))
            return jsonify({'result': result, 'node_status': node_status, 'node_name': str(name)})
        except docker.errors.NotFound:
            # pod doesn't exist - can't create node
            result = str(pod_name) + " not found"
            return jsonify({'result': result, 'node_status': 'not created', 'node_name': str(name)})
        
@app.route('/cloudproxy/nodes/rm/<name>', methods=['GET'])   
def cloud_node_rm(name):
    if request.method == 'GET':
        print('Request to remove node: ' + str(name))
        try:
            # if node exists
            node_to_remove = client.containers.get(name)
            for i in range(len(nodes)):
                if name == nodes[i].name:
                    # remove if status is idle
                    if nodes[i].status == 'Idle':
                        node_to_remove.stop()
                        node_to_remove.remove() 
                        result = 'successfully removed node: ' + str(name)
                        # remove the node from list of nodes as well
                        del nodes[i]
                        return jsonify({'result': result})
                    # reject if not idle
                    else:
                        result = 'node ' + str(name) + ' status is not Idle'
                        return jsonify({'result': result})
            result = 'node ' + str(name) + ' was not instantiated for this cloud.'
            return jsonify({'result': result})
        except docker.errors.NotFound:
            # node doesn't exist - can't delete
            result = str(name) + ' not found'
            return jsonify({'result': result})
        
@app.route('/cloudproxy/jobs/launch', methods=['POST'])
def cloud_launch():
    if request.method == 'POST':
        file = request.files['files']
        # Create Job instance and print id
        job = Job(file, "Registered")
        jobs.append(job)
        print('Request to launch job: ' + str(job.id))
        # Look for available node
        for node in nodes:
            if node.status == "Idle":
                try:
                    container = client.containers.get(node.name)
                    # Set node & job status as "Running"
                    job.status = "Running"
                    for i in range(len(jobs)):
                        if job.id == jobs[i].id:
                            jobs[i].status = "Running"
                    node.status = "Running"
                    print('Job dispatched: ' + str(job.id))
                    # Assgin job to the node
                    job.node_id = node.id
                    # Run the job
                    commands = file.readlines()
                    command_str = commands[0].decode("ascii")
                    for i, command in enumerate(commands):
                        if i > 0:
                             command_str = command_str[:(len(command_str)-1)] + "; " + command.decode("ascii")
                    (exec_code, output) = container.exec_run(command_str)
                    # Append output
                    node.jobs_output.append(str({'job_id':job.id, 'output':output}))
                    print("output appended to " + node.id)
                    # Update status when done running
                    job.status = "Completed"
                    for i in range(len(jobs)):
                        if job.id == jobs[i].id:
                            jobs[i].status = "Completed"
                    node.status = "Idle"
                    result = 'Job ' + str(job.id) + ' is completed'
                    return jsonify({'result': result})
                except docker.errors.NotFound:
                    print(node.name, ' not found')
                    continue
        # job_dispatch handles case when all nodes are busy
        # it runs separately from the API to go through the queue and run the jobs that are waiting for an available node
        job_queue.append(job)
        return jsonify({'result': 'all nodes are busy, your job will run once a node becomes available'})

@app.route('/cloudproxy/jobs/abort/<job_id>', methods=['GET'])    
def cloud_abort(job_id):
    if request.method == 'GET':
        print('Request to abort job: ' + str(job_id))
        for i in range(len(job_queue)):
            if job_queue[i].id == job_id:
                # Job registered, remove job from queue
                if job_queue[i].status == "Registered":
                    del job_queue[i]
                    for j in range(len(jobs)):
                        if jobs[j].id == job_id:
                            jobs[j].status = "Aborted"
                    result = 'Job ' + str(job_id) + ' is aborted'
                    return jsonify({'result': result})
                # Job completed
                elif job_queue[i].status == "Completed":
                    result = 'Job ' + str(job_id) + " cannot be aborted. It has been completed."
                    return jsonify({'result': result})
                # Job running
                elif job_queue[i].status == "Running":
                    for node in nodes:
                        if node.id == job_queue[i].node_id:
                            try:
                                container = client.containers.get(node.name)
                                container.stop()
                                node.status = "Idle"
                                job_queue[i].status = "Aborted"
                                result = 'Job ' + str(job_id) + 'is aborted'
                                return jsonify({'result': result})
                            except docker.errors.NotFound:
                                result = 'Container ' + str(node.name) + ' for job ' + str(job_id) + ' not found'
                                return jsonify({'result': result})
                    for j in range(len(jobs)):
                        if jobs[j].id == job_id:
                            jobs[j].status = "Aborted"
                    result = 'Node ' + str(job.node_id) + ' for job' + str(job_id) + ' not found'
                    return jsonify({'result': result})
        # Job not found in the queue
        for i in range(len(jobs)):
            if jobs[i].id == job_id:
                if jobs[i].status == "Completed":
                    result = 'Job' + str(job_id) + "cannot be aborted. It has been completed."
                    return jsonify({'result': result})
        result = 'Job ' + str(job_id) + " not found."
        return jsonify({'result': result})

# ------------------------MONITORING-------------------------

@app.route('/cloudproxy/pods/all', methods=['GET'])
def cloud_pod_ls():
    # for the moment, only default node is queryed since clusters are not supported
    # for pod in pods:
    # the name, ID and number of nodes attached to it must be printed to stdout
    pod = client.networks.get('default_pod')
    return jsonify({'pod_name':pod.name, 'pod_id':pod.id, 'num_nodes':str(len(pod.containers))})

@app.route('/cloudproxy/nodes/all', methods=['GET'])
def cloud_node_ls_all():
    result = []
    for node in nodes:
    # name, ID and status must be printed to stdout
        n = {'node_name':node.name, 'node_id':node.id, 'status':node.status}
        result.append(n)
    return jsonify(result)

@app.route('/cloudproxy/nodes/<pod_id>', methods=['GET'])
def cloud_node_ls(pod_id):
    result = []
    for node in nodes:
    # name, ID and status must be printed to stdout
    # currently only accomodates one resource pod -- need to change for future cluster
        n = {'node_name':node.name, 'node_id':node.id, 'status':node.status}
        result.append(n)
    return jsonify(result)

@app.route('/cloudproxy/jobs/all', methods=['GET'])
def cloud_job_ls_all():
    #the name, ID, node ID (if assigned to a node) and status
    result = []
    for job in jobs:
        if job.node_id != "":
            j = {'job_name':job.name,'job_id':job.id,'node_id':job.node_id,'status':job.status}
            result.append(j)
    return jsonify(result)

@app.route('/cloudproxy/jobs/<node_id>', methods=['GET'])
def cloud_job_ls(node_id):
    #the name, ID, node ID (if assigned to a node) and status
    result = []
    for job in jobs:
        if job.node_id == node_id:
            j = {'job_name':job.name,'job_id':job.id,'node_id':job.node_id,'status':job.status}
            result.append(j)
    return jsonify(result)

@app.route('/cloudproxy/jobs/log/<job_id>', methods=['GET'])
def cloud_job_log(job_id):
    # prints out the log of a specified job
    result = []
    node_id = ""
    for job in jobs:
        if job.id == job_id:
            node_id = job.node_id
            break
    for node in nodes:
        if node.id == node_id:
            result = node.jobs_output
            break
    return jsonify(result)

@app.route('/cloudproxy/nodes/log/<node_id>', methods=['GET'])
def cloud_log_node(node_id):
    # prints out the entire log of a specified node
    result = []
    for node in nodes:
        if node.id == node_id:
            result = node.jobs_output
            break
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
