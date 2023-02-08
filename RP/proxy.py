from flask import Flask, jsonify, request
import docker
import time

app = Flask(__name__)
client = docker.from_env()

nodes = []
jobs = []


# TODO: this file needs to contain all possible api calls that need docker commands
# includes: resource manager and resource monitor api calls

# ------------------------ALICE-------------------------

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
        time.sleep(5)
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
            # TODO: need a better way of keeping track of all nodes status (from monitoring i think)
            result = 'unknown'
            node_status = 'unknown'
            for node in nodes:
                if name == node['name']:
                    print('Node already exists: ' + node['name'] + ' with status ' + node['status'])
            if result == 'unknown' and node_status == 'unknown':
                n = client.containers.run(image="alpine", detach=True, network=pod.name)
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


# ------------------------JOSHUA-------------------------

@app.route('/cloudproxy/nodes/all')
def cloud_get_all_nodes():
    # TODO: loop through all nodes and add them to the json
    if request.method == 'GET':

        nodes_list = client.network.containers.list(all=True)
        return jsonify(nodes_list)

@app.route('/cloudproxy/nodes/<pod_id>')
def cloud_get_all_nodes(pod_id):
    if request.method == 'GET':
        network = client.networks.get(pod_id)
        return jsonify(network.containers.list(all=True))

@app.route('/cloudproxy/jobs/all')
def cloud_get_all_nodes():
    # TODO: loop through all nodes and add them to the json
    if request.method == 'GET':
        return jsonify(jobs)

# @app.route('/cloudproxy/jobs/<node_id>')
# def cloud_get_all_nodes(node_id):
#     # TODO: loop through all nodes and add them to the json
#     if request.method == 'GET':
#         for job in jobs:
#             if job.id == job_id:
#                 return jsonify(job)

@app.route('/cloudproxy/pods/all')
def cloud_get_all_pods():
    pods = client.networks.list()
    response = requests.get('/cloud/pods/' + pods[0]).json()
    for pod in pods[1:]:
        response.update(requests.get('/cloud/pods/' + str(pod)).json())
    return response

@app.route('/cloudproxy/pods/job_numbers')
def cloud_get_all_pods_job_numbers():
    pods = client.networks.list()
    num_jobs = []
    for pod in pods:
        network = client.networks.get(pod.name)
        num_jobs.append(len(network.containers))

    return num_jobs



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)