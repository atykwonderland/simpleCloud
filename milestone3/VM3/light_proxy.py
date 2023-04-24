import requests
import docker
from flask import Flask, jsonify, request
import os
import sys
import time

app = Flask(__name__)

client = docker.from_env()

MAX_LIGHT_NODES = 20
AVAIL_CPUS = 0

nodes = []

# node is container in docker
class Node:
    def __init__(self, name, id, status, port) -> None:
        self.name = name
        self.status = status
        self.id = id
        self.port = port

#------------------------TOOLSET-------------------------

@app.route('/cloudproxy/init')
def cloud_init():
    print('Request to initialize light pod')
    id = -1
    try:
        # if light pod doesn't already exist
        pod = client.networks.get('light_pod')
        result = str(pod.name) + ' was already created.'
        id = pod.id
    except docker.errors.NotFound:
        # create light pod
        pod = client.networks.create('light_pod', driver='bridge')
        result = str(pod.name) + ' was newly created.'
        id = pod.id
    
    # set node limit
    MAX_LIGHT_NODES = 20
    # set available CPUs
    AVAIL_CPUS = os.cpu_count()

    # check if everything is ready for job
    p = '/home/comp598-user/milestone2/'
    dirpaths  = [f.path for f in os.scandir('/home/comp598-user/milestone2') if f.is_dir()]
    print(dirpaths)
    fp_error = False
    if p + 'light' in dirpaths:
        filepaths = [f.path for f in os.scandir(p + 'light') if f.is_file()]
        if p + 'light/Dockerfile' in filepaths:
            app_dirpaths  = [f.path for f in os.scandir(p + 'light') if f.is_dir()]
            if p + 'light/app' in app_dirpaths:
                app_filepaths = [f.path for f in os.scandir(p + 'light/app') if f.is_file()]
                if (p + 'light/app/app.py' not in app_filepaths) or (p + 'light/app/requirements.txt' not in app_filepaths):
                    fp_error = True
            else:
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
                    'name': 'light_pod'})

@app.route('/cloudproxy/node/register/<name>/<pod_name>') 
def cloud_node(name, pod_name):
    print('Request to register new node: ' + str(name) + ' in pod ' + str(pod_name))
    try:
        # check if pod exists
        pod = client.networks.get(pod_name)
        result = 'unknown'
        node_status = 'unknown'
        # check if the limit of the pod has been met
        if len(nodes) >= MAX_LIGHT_NODES:
            print('Pod ' + str(pod_name) + ' is already at its maximum resource capacity')
            result = 'pod at maximum reasource capacity'
            response = 'failure'
            return jsonify({'response': response, 'result': result, 'node_status': 'not created', "name": str(name), 'pod_name': str(pod_name)})
        for node in nodes:
            # node already exists
            if name == node.name:
                node_status = node.status
                print('Node already exists: ' + str(name) + ' with status ' + str(node_status))
                result = 'node already exists'
                response = 'failure'
                return jsonify({'response': 'failure', 'result': result, 'node_status': 'not created', "name": str(name), 'pod_name': str(pod_name)})
        # make new node
        if result == 'unknown' and node_status == 'unknown':
            n = client.containers.run(image = "alpine", command='/bin/sh', detach=True, tty=True, name=str(name), network=pod_name)
            node_status = 'New'
            nodes.append(Node(name, n.id, node_status, None))
            result = 'node_added'
            response = 'success'
            print('Successfully added a new node: ' + str(name) + ' to pod ' + str(pod_name))
        return jsonify({'response': response, 'result': result, 'node_status': node_status, "name": str(name), 'pod_name': str(pod_name)})
    except docker.errors.NotFound:
        # pod doesn't exist - can't create node
        result = str(pod_name) + " not found"
        response = 'failure'
        return jsonify({'response': response, 'result': result, 'node_status': 'not created', "name": str(name), 'pod_name': str(pod_name)})

@app.route('/cloudproxy/node/remove/<name>/<pod_name>')   
def cloud_pod_node_rm(name, pod_name):
    print('Request to remove node: ' + str(name) + ' from pod ' + str(pod_name))
    try:
        # if node exists
        node_to_remove = client.containers.get(name)
        for i in range(len(nodes)):
            if name == nodes[i].name:
                # remove if status is new
                if nodes[i].status == 'New':
                    node_to_remove.stop()
                    node_to_remove.remove() 
                    result = 'successfully removed node: ' + str(name) + ' from pod ' + str(pod_name)
                    response = 'success'
                    # remove the node from list of nodes as well
                    del nodes[i]
                    return jsonify({'response': response, 'result': result, 'node_status': 'Removed', 'name': str(name), 'pod_name': str(pod_name)})
                elif nodes[i].status == 'Online':
                    node_to_remove.stop()
                    node_to_remove.remove()
                    del nodes[i]
                    result = 'successfully removed node: ' + str(name) + 'from pod' + str(pod_name)
                    response = 'success'
                    return jsonify({'response': response, 'result': result, 'node_status': 'Removed', 'name': str(name), 'pod_name': str(pod_name)})
        result = 'node ' + str(name) + ' was not instantiated for this cloud.'
        response = 'failure'
        print(response)
        return jsonify({'response': response, 'result': result, 'node_status': 'not removed', 'name': str(name), 'pod_name': str(pod_name)})
    except docker.errors.NotFound:
        # node doesn't exist - can't delete
        result = str(name) + ' not found'
        response = 'failure'
        return jsonify({'response': response, 'result': result, 'node_status': 'not removed', 'name': str(name), 'pod_name': str(pod_name)})

@app.route('/cloudproxy/pod/launch')
def launch():
    print('Request to launch pod: light_pod')
    for node in nodes:
        if node.status == 'New':
            [img, logs] = client.images.build(path='/home/comp598-user/milestone2/light/', rm=True, dockerfile='/home/comp598-user/milestone2/light/Dockerfile')
            for container in client.containers.list():
                if container.name == node.name:
                    container.remove(v=True, force=True)
            port = 7000
            taken = True
            while(taken):
                port = port + 1
                taken = False
                for i in range(len(nodes)):
                    if nodes[i].port == port:
                        taken = True  
            client.containers.run(image=img,
                                  detach=True,
                                  name=node.name,
                                  network='light_pod',
                                  mem_limit='100m',
                                  cpu_quota=int(AVAIL_CPUS * 0.3 * 100000),
                                  cpu_period=100000,
                                  command=['python','app.py',node.name],
                                  ports={'5000/tcp': port})
            node.status = 'Online'
            node.port = port
            return jsonify({'response': 'success',
                            'name': node.name,
                            'port': node.port, 
                            'online': True})

    return jsonify({'response': 'failure',
                    'reason': 'No node available'})

#------------------------TOOLSET-------------------------

#------------------------ELASTICITY-------------------------

@app.route('/cloudproxy/compute_usage')
def compute_usage():
    cpu_avg = 0
    mem_avg = 0
    try:
        networks_list = client.networks.list(names=['light_pod'])
        ident = networks_list[0].id
        network = client.networks.get(ident)
        containers_list = network.containers
        num_containers = len(containers_list)

        for container in containers_list:
            info = container.stats(stream=False)
            cpu_info = info['cpu_stats']
            prev_cpu_info = info['precpu_stats']
            mem_info = info['memory_stats']

            cpu_delta = float(cpu_info['cpu_usage']['total_usage']) - float(prev_cpu_info['cpu_usage']['total_usage'])
            system_cpu_delta = float(cpu_info['system_cpu_usage']) - float(prev_cpu_info['system_cpu_usage'])
            cpu_usage = float((cpu_delta / system_cpu_delta) * 100.0)
            cpu_avg += cpu_usage

            used_memory = float(mem_info['usage'])
            available_memory = float(mem_info['limit'])
            mem_usage = float((used_memory / available_memory) * 100.0)
            mem_avg += mem_usage

        if num_containers != 0:
            cpu_avg = cpu_avg / num_containers
            mem_avg = mem_avg / num_containers
            
    except:
        return jsonify({'response': 'failure', 'reason': 'could not get pod'})                                         

    return jsonify({'response':'success', 'cpu_avg':cpu_avg, 'mem_avg': mem_avg})                                        

#------------------------ELASTICITY-------------------------

#------------------------MONITORING-------------------------

@app.route('/cloudproxy/nodes')
def cloud_node_ls():
    result = []
    for node in nodes:
        n = {'node_name':node.name, 'node_id':node.id, 'status':node.status}
        result.append(n)
    return jsonify(result)

#------------------------MONITORING-------------------------

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6002)
