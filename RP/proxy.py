from flask import Flask, jsonify, request
import docker
import time

app = Flask(__name__)
client = docker.from_env()

nodes = []
jobs = []

# TODO: this file needs to contain all possible api calls that need docker commands 
# includes: resource manager and resource monitor api calls

#------------------------ALICE-------------------------

# TODO: This won't ever return? not sure about this implementation (from tutorial though)
@app.route('/cloudproxy/init')
def cloud_init():
    try:
        network = client.networks.get('default')
    except docker.errors.NotFound:
        network = client.networks.create('default', driver='bridge')

    print(client.api.inspect_network(network.id))
    print('Manager waiting on containers to connect to the default bridge...')
    while len(network.containers) == 0:
        time.sleep (5)
        network.reload()

    container_list = []
    while 1:
        if not container_list == network.containers:
            container_list = network.containers
            for container in container_list:
                print("Container connected: \n\tName:" + container.name + "\n\tStatus: " + container.status + "\n")
                time.sleep(5)
                network.reload()

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
            #TODO: need a better way of keeping track of all nodes status (from monitoring i think)
            result = 'unknown'
            node_status = 'unknown'
            for node in nodes:
                if name == node['name']:
                    print('Node already exists: ' + node['name'] + ' with status ' + node['status'])
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image = "alpine", detach=True, network=pod.name)
                result = 'node_added'
                nodes.append({'name': name, 'status': 'IDLE'})
                node_status = 'IDLE'
                print('Successfully added a new node: ' + str(name))
            return jsonify({'result': result, 'node_status': node_status, 'node_name': name})
        except docker.errors.NotFound:
            result = str(pod_name) + " not found"
        return jsonify({'result': result})
        
@app.route('/cloud/nodes/<name>', methods=['DELETE'])   
def cloud_node_rm(name):
    if request.method == 'GET':
        try:
            # if node exists
            node_to_remove = client.containers.get(name)
            for i, node in nodes:
                if name == node['name']:
                    # remove if status is idle
                    if node['status'] == 'IDLE':
                        node_to_remove.remove() 
                        result = 'successfully removed node: ' + str(name)
                        # remove the node from local list of nodes
                        del nodes[i]
                        break
                    # reject if not idle
                    else:
                        result = 'node ' + str(name) + ' status is not IDLE'
                        break           
        except docker.errors.NotFound:
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
                    node.jobs_output.append(job.id, logs_file)
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
                result = 'Job ' +str(job_id) + " cannot be aborted. It has been completed.")
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
    result = 'Job ' + str(job_id) + " not found.")
    return jsonify({'result': result})
#-------------------------------------------------

@app.route('/cloudproxy/nodes/all')
def cloud_get_all_nodes():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
