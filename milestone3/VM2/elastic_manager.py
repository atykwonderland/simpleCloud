import time
from flask import Flask, jsonify, request 
import requests
import pycurl 
import json 
import subprocess
from io import BytesIO
from datetime import datetime
from multiprocessing import Process, Pipe

light_proxy = 'http://10.140.17.109:6002'
medium_proxy = 'http://10.140.17.109:6003'
heavy_proxy = 'http://10.140.17.109:6001'
resource_manager = 'http://10.140.17.108:6002'

thresholds = {
    'light_pod': {'upper':None, 'lower':None},
    'medium_pod': {'upper':None, 'lower':None},
    'heavy_pod': {'upper':None, 'lower':None}
}
pod_limits = {
    'light_pod': {'upper':20, 'lower':0},
    'medium_pod': {'upper':15, 'lower':0},
    'heavy_pod': {'upper':10, 'lower':0}
}
processes = {
    'light_pod': None,
    'medium_pod': None,
    'heavy_pod': None
}

cURL = pycurl.Curl()
app = Flask(__name__)

#TODO
parent_light, child_light = Pipe()
parent_medium, child_medium = Pipe()
parent_heavy, child_heavy = Pipe()

def compute_usage(pod_name):
    if pod_name == "light_pod":
        pod_URL = light_proxy
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy

    buffer = bytearray()
    cURL.setopt(cURL.URL, pod_URL + '/cloudproxy/compute_usage')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    usage = json.loads(buffer.decode())
    return usage

def get_nodes(pod_name):
    # getting the nodes (list of dictionaries)
    if pod_name == "light_pod":
        pod_URL = light_proxy
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy

    buffer = bytearray()
    cURL.setopt(cURL.URL, pod_URL + '/cloudproxy/nodes')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    nodes = json.loads(buffer.decode())
    return nodes
    
def get_pod_id(pod_name):
    buffer = bytearray()
    cURL.setopt(cURL.URL, resource_manager + '/cloud/pods/all')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    pods = json.loads(buffer.decode())
    for pod in pods:
        if pod['name'] == pod_name:
            pod_id = pod['id']
            break
    return pod_id

def register_launch_node(pod_id, node_name):
    buffer = bytearray()
    cURL.setopt(cURL.URL, resource_manager + '/cloud/node/register/' + str(node_name) + '/' + str(pod_id) + '/True')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    buffer = bytearray()
    cURL.setopt(cURL.URL, resource_manager + '/cloud/pod/launch/' + str(pod_id) + '/True')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

def remove_node(pod_id, node_name):
    buffer = bytearray()
    cURL.setopt(cURL.URL, resource_manager + '/cloud/node/remove/'+ str(node_name) + '/' + str(pod_id))
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

def manage_proxy_elasticity(pod_name, parent):
    time.sleep(5)

    nodes = get_nodes(pod_name)
    pod_id = get_pod_id(pod_name)

    if len(nodes) > pod_limits[pod_name]['upper']:
        diff = len(nodes) - pod_limits[pod_name]['upper']
        while diff > 0:
            remove_node(pod_id, nodes[diff]['node_name'])
            diff -= 1
    elif len(nodes) < pod_limits[pod_name]['lower']:
        diff = pod_limits[pod_name]['lower'] - len(nodes)
        while diff > 0:
            register_launch_node(pod_id, 'elastic_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            diff -= 1

    while(True):
        #TODO
        if parent.poll():
            msg = parent.recv()
            thresholds[msg[0]][msg[1]]=float(msg[2])

        nodes = get_nodes(pod_name)
        pod_id = get_pod_id(pod_name)
        cpu_avg = compute_usage(pod_name)['cpu_avg'] # average per node in pod
        curr_len = len(nodes)

        # adjust based off of CPU
        if thresholds[pod_name]['lower'] is not None:
            while(cpu_avg < thresholds[pod_name]['lower']):
                if (curr_len > pod_limits[pod_name]['lower']):
                    print(nodes[int(curr_len - 1)]['node_name'])
                    remove_node(pod_id, nodes[int(curr_len - 1)]['node_name'])
                    curr_len -= 1
                    cpu_avg = compute_usage(pod_name)['cpu_avg']   # re-compute the usage, since it will have changed
                else:
                    break

        if thresholds[pod_name]['upper'] is not None:
            while(cpu_avg > thresholds[pod_name]['upper']):
                if (curr_len < pod_limits[pod_name]['upper']):
                    register_launch_node(pod_id, 'elastic_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                    curr_len += 1
                    cpu_avg = compute_usage(pod_name)['cpu_avg']   # re-compute the usage, since it will have changed
                else:
                    break

        time.sleep(10)
    return 
        
@app.route('/cloudelastic/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable(pod_name, lower, upper):
    if pod_name == 'light_pod' or pod_name == 'medium_pod' or pod_name == 'heavy_pod':
        pod_limits[pod_name]['upper'] = int(upper)
        pod_limits[pod_name]['lower'] = int(lower)

        nodes = get_nodes(pod_name)
        pod_id = get_pod_id(pod_name)

#TODO   
        if pod_name == 'light_pod':
            task = Process(target=manage_proxy_elasticity,  args=(pod_name,child_light,))
        elif pod_name == 'medium_pod':
            task = Process(target=manage_proxy_elasticity,  args=(pod_name,child_medium,))
        elif pod_name == 'heavy_pod':
            task = Process(target=manage_proxy_elasticity,  args=(pod_name,child_heavy,))
        processes[pod_name] = task
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    
    return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
   
@app.route('/cloudelastic/elasticity/disable/<pod_name>')
def cloud_elasticity_disable(pod_name):
    print('Request to disable elasticity for pod: '  + str(pod_name))
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        process = processes[pod_name]
        process.kill()
        processes[pod_name] = None
        thresholds[pod_name]['upper'] = None 
        thresholds[pod_name]['lower'] = None 
        return jsonify({'response': 'success',
                        'reason': 'successfully disabled elasticity for pod ' + pod_name})
    
    return jsonify({'response': 'failure',
                    'reason': 'pod not found'})

@app.route('/cloudelastic/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower(pod_name, value):
    # set threshold value for pod
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        thresholds[pod_name]['lower'] = value

        #TODO
        if pod_name == 'light_pod':
            parent_light.send([pod_name, 'lower', value])
        elif pod_name == 'medium_pod':
            parent_medium.send([pod_name, 'lower', value])
        elif pod_name == 'heavy_pod':
            parent_medium.send([pod_name, 'lower', value])

    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
    
    return jsonify({'response': 'success',
                    'result': 'lower threshold set to: ' + str(value)})

@app.route('/cloudelastic/elasticity/upper/<pod_name>/<value>')
def cloud_elasticity_upper(pod_name, value):
    # set threshold value for pod
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        thresholds[pod_name]['upper'] = value

    #TODO
        if pod_name == 'light_pod':
            parent_light.send([pod_name, 'upper', value])
        elif pod_name == 'medium_pod':
            parent_medium.send([pod_name, 'upper', value])
        elif pod_name == 'heavy_pod':
            parent_medium.send([pod_name, 'upper', value])
        
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
    
    return jsonify({'response': 'success',
                    'result': 'upper threshold set to: ' + str(value)})

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6004)
