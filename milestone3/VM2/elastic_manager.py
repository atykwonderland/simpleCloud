#TODO


from flask import Flask, jsonify, request 
import requests
import pycurl 
import json 
import subprocess
from io import BytesIO
import datetime

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

cURL = pycurl.Curl()
app = Flask(__name__)

#TODO
@app.route('/cloudelastic/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower():
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

@app.route('/cloudelastic/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable():
    pass

@app.route('/cloudelastic/elasticity/lower/<pod_name>')
def cloud_elasticity_disable():
    pass

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5002)

def compute_usage(pod_name):

    buffer = bytearray()
    cURL.setopt(cURL.URL, pod_name + '/cloudproxy/compute_usage')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    cpu_usage = json.loads(buffer.decode())
    cpu_usage = usage['response']
    return cpu_usage

def manage_light():
    cpu_usage = compute_usage('light_proxy')        
    # remove a node by setting it to "NEW"
    while cpu_usage < value:
        for node in response_json: # need to get a list of nodes
            if node['status'] == "Online" and cpu_usage < value:
                # need to call the proxy to turn the nodes on and off. 
                # to add more nodes, call register and then launch, to remove then you can call remove
                command = "echo 'experimental-mode on; set server " + server_type +"/"+ node['node_name'] + " state maint' | sudo socat stdio /run/haproxy/admin.sock" 
                subprocess.run(command, shell=True, check=True)
                node['status'] == "NEW"
            cpu_usage = compute_usage()   # re-compute the usage, since it will have changed
