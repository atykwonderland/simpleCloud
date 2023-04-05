import time
from flask import Flask, jsonify, request 
import requests
import pycurl 
import json 
import subprocess
from io import BytesIO
import datetime
from multiprocessing import Process

light_proxy = 'http://10.140.17.109:6001'
medium_proxy = 'http://10.140.17.109:6002'
heavy_proxy = 'http://10.140.17.109:6003'

thresholds = {
    'light_pod': {'upper':None, 'lower':None},
    'medium_pod': {'upper':None, 'lower':None},
    'heavy_pod': {'upper':None, 'lower':None}
}
pod_limits = {
    'light_pod': {'upper':None, 'lower':None},
    'medium_pod': {'upper':None, 'lower':None},
    'heavy_pod': {'upper':None, 'lower':None}
}

processes = {
    'light_pod': None,
    'medium_pod': None,
    'heavy_pod': None
}

cURL = pycurl.Curl()
app = Flask(__name__)

@app.route('/cloudelastic/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower(pod_name, value):
    # set threshold value for pod
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        thresholds[pod_name]['lower'] = value
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
    
    # trigger thread to refresh?

    return jsonify({'response': 'success',
                    'result': 'lower threshold set to: ' + str(value)})

@app.route('/cloudelastic/elasticity/upper/<pod_name>/<value>')
def cloud_elasticity_upper(pod_name, value):
    # set threshold value for pod
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        thresholds[pod_name]['upper'] = value
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
    
    # trigger thread to refresh?

    return jsonify({'response': 'success',
                    'result': 'upper threshold set to: ' + str(value)})

def compute_usage(pod_name):
    buffer = bytearray()
    cURL.setopt(cURL.URL, pod_name + '/cloudproxy/compute_usage')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    usage = json.loads(buffer.decode())
    cpu_usage = usage['response']
    return cpu_usage

def get_nodes(pod_name):
    # getting the nodes (list of dictionaries)
    buffer = bytearray()
    cURL.setopt(cURL.URL, pod_name + '/cloudproxy/nodes')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    nodes = json.loads(buffer.decode())
    nodes = nodes['response']
    
def get_pod_id(pod_name):
    buffer = bytearray()
    cURL.setopt(cURL.URL,'/cloud/pods/all')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    pods = json.loads(buffer.decode())
    pods = pods['response']
    for pod in pods:
        if pod['name'] == pod_name:
            pod_id = pod['id']
            break

def manage_proxy_elasticity(pod_name):

    while(True):
       
        cpu_usage = compute_usage(pod_name) # average per node in pod
        nodes = get_nodes(pod_name)
        pod_id = get_pod_id(pod_name)
        
        for node in nodes: # need to get a list of nodes
            try:
                if node['status'] == "Online" and cpu_usage < thresholds[pod_name]['lower']:
                    # need to call the proxy to turn the nodes on and off. 
                    # to add more nodes, call register and then launch, to remove then you can call remove
                    buffer = bytearray()
                    cURL.setopt(cURL.URL,'/cloud/node/remove/'+node['node_name']+'/'+pod_id)
                    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
                    cURL.perform()
                                        
                elif node['status'] == "Online" and cpu_usage > thresholds[pod_name]['upper']:
                    # need to call the proxy to turn the nodes on and off. 
                    # to add more nodes, call register and then launch, to remove then you can call remove
                    buffer = bytearray()
                    cURL.setopt(cURL.URL,'/cloud/node/register/'+node['node_name']+'/'+pod_id)
                    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
                    cURL.perform()

                    buffer = bytearray()
                    cURL.setopt(cURL.URL,'/cloud/pod/launch/'+pod_id)
                    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
                    cURL.perform()
                                        
                cpu_usage = compute_usage(pod_name)   # re-compute the usage, since it will have changed
            except:
                continue
        time.sleep(10)
    return 
        
@app.route('/cloudelastic/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable(pod_name, lower, upper):
    if pod_name == 'light_pod' or pod_name == 'medium_pod' or pod_name == 'heavy_pod':
        pod_limits[pod_name]['upper'] = upper
        pod_limits[[pod_name]['lower'] = lower
        task = Process(target=manage_proxy_elasticity,  args=(pod_name))
        processes[pod_name] = task
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
   

@app.route('/cloudelastic/elasticity/disable/<pod_name>')
def cloud_elasticity_disable(pod_name):
    print('Request to disable elasticity for pod: '  + str(pod_name))
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        process = processes[pod_name]
        process.kill()
        return jsonify({'response': 'success',
                        'reason': 'successfully disabled elasticity for pod ' + pod_name})
    return jsonify({'response': 'failure',
                    'reason': 'pod not found'})

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5002)
