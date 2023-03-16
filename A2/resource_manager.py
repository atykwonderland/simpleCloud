from flask import Flask, jsonify, request 
import sys 
import pycurl 
import json 
import subprocess
from io import BytesIO
import requests

light_proxy = 'http://10.140.17.108:5001'
medium_proxy = 'http://10.140.17.107:5001'
heavy_proxy = 'http://10.140.17.109:5001'
monitor = 'http://winter2023-comp598-group03-02.cs.mcgill.ca:7000'

# {name, id}
pods = []

cURL = pycurl.Curl()
app = Flask(__name__)

#------------------------TOOLSET-------------------------

@app.route('/cloud/init')
def cloud_init():
    print('Request to initialize cloud')
    buffer = bytearray()

    print('Initializing light pod')
    cURL.setopt(cURL.URL, light_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing light pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})

    print('Initializing medium pod')
    cURL.setopt(cURL.URL, medium_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing medium pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})

    print('Initializing heavy pod')
    cURL.setopt(cURL.URL, heavy_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing heavy pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})
            
    return jsonify({'response': 'success'}) 

@app.route('/cloud/node/register/<name>/<pod_id>')
def register_node(name, pod_id):
    found = False
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id:
            pod_name = pod['name']
            found = True
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})
    if pod_name == 'light_pod':
        cURL.setopt(cURL.URL,  light_proxy + '/register/' + name + '/' + pod_name)
    elif pod_name == 'medium_pod':
        cURL.setopt(cURL.URL,  medium_proxy + '/register/' + name + '/' + pod_name)
    elif pod_name == 'heavy_pod':
        cURL.setopt(cURL.URL,  heavy_proxy + '/register/' + name + '/' + pod_name)
    buffer = bytearray()
    
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perfrom()
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            pod_name = response_dictionary['pod_name']
            name = response_dictionary['name']
            running = response_dictionary['running']
            return jsonify({'response': 'success',
                            #'port': port,
                            'name': name,
                            'running': running})
    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/cloud/node/remove/<name>/<pod_id>')
def remove_node(name, pod_id):
    found = False
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id:
            pod_name = pod['name']
            found = True
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})
    if pod_name == 'light_pod':
        cURL.setopt(cURL.URL,  light_proxy + '/rm/' + name + '/' + pod_name)
    elif pod_name == 'medium_pod':
        cURL.setopt(cURL.URL,  medium_proxy + '/rm/' + name + '/' + pod_name)
    elif pod_name == 'heavy_pod':
        cURL.setopt(cURL.URL,  heavy_proxy + '/rm/' + name + '/' + pod_name)
    buffer = bytearray()
    
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perfrom()
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            #port = response_dictionary['port']
            name = response_dictionary['name']
            running = response_dictionary['running']
            if running:
                disable_command = "echo 'experimental-mode on; set server servers/'" + name + ' state maint ' + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(disable_command, shell=True, check=True)
                
                command = "echo 'experimental-mode on; set server servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(command, shell=True, check=True)
                return jsonify({'response': 'success',
                                #'port': port,
                                'name': name,
                                'running': running})
    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/cloud/pods/resume/<pod_id>')
def cloud_resume(pod_id):
    found = False
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id:
            pod_name = pod['name']
            found = True
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})
    
    if pod_name == "light_pod":
        pod_URL = light_proxy
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy

    # get the nodes associated with the pod
    data = BytesIO()
    cURL.setopt(cURL.pod_URL, monitor + '/cloudmonitor/nodes/' + str(pod_id))
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dictionary = json.loads(data.getvalue())
    print(dictionary)
    nodes = dictionary['result']
    for node_id in [x for x in nodes if x['status'] == "online"]:
        command1 = "echo 'experimental-mode on; add server " + pod_URL + "/" + node_id + "' | sudo socat stdio /var/run/haproxy.sock"
        subprocess.run(command1, shell=True, check=True)
        # need to update this address.
        command2 = "echo 'experimental-mode on; enable server " + pod_URL + "/" + node_id + "' | sudo socat stdio /var/run/haproxy.sock'"
        subprocess.run(command2, shell=True, check=True)
         
@app.route('/cloud/pods/pause/<pod_id>')
def cloud_pause(pod_id):
    found = False
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id:
            pod_name = pod['name']
            found = True
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})
    
    if pod_name == "light_pod":
        pod_URL = light_proxy
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy
    
    # get the nodes associated with the pod
    data = BytesIO()
    cURL.setopt(cURL.URL, monitor + '/cloudmonitor/nodes/' + str(pod_id))
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dictionary = json.loads(data.getvalue())
    print(dictionary)
    nodes = dictionary['result']
        
    # remove the nodes that are online     
    for node_id in [x for x in nodes if x['status'] == "online"]:
        data = BytesIO()
        cURL.setopt(cURL.URL, pod_URL + '/cloudproxy/nodes/rm/' + str(node_id))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)
        result = dictionary['result']
        
    # disable the server
    for node_id in [x for x in nodes if x['status'] != "online"]:
        command = "echo 'experimental-mode on; disable server " + pod_URL + "/" + node_id + "' | sudo socat stdio /var/run/haproxy.sock"
        subprocess.run(command, shell=True, check=True)
        # is the way that I added the node_id correct?
        
@app.route('/launch/<pod_id>')
def launch(pod_id):
    
#     You run the cloud launch JOB and it puts the state of the node as ONLINE and starts the web server. 
#     Also, the cloud launch informs the load balancer about the new node. 
#     After this point the load balancer has the new node available for taking workload requests.

    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id: 
            pod_name = pod['name']
    
    if pod_name == "light_pod":
        pod_URL = light_proxy
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy

    cURL.setopt(cURL.URL, pod_URL + '/launch')
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            port = response_dictionary['port']
            name = response_dictionary['name']
            online = response_dictionary['online']
            print('port: ' + port)
            if online:
                command1 = "echo 'experimental-mode on; add server light-servers/'" + name + ' ' + pod_URL[7:-5] + ':' + port + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(command1, shell=True, check=True)
                
                command2 = "echo 'experimental-mode on; set server light-servers/'" + name + ' state ready ' + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(command2, shell=True, check=True) 
                return jsonify({'response': 'success',
                                'port': port,
                                'name': name,
                                'online': online})
    
    return jsonify({'response': 'failure',
                    'reason': 'Unknown'})

#------------------------TOOLSET-------------------------

#------------------------MONITORING-------------------------

@app.route('/cloud/pods/all')
def cloud_pod_ls():
    print('Request to list all pods')
    return jsonify(pods)

#------------------------MONITORING-------------------------


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6001)
