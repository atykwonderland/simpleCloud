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

# {name, id, isElastic, upper, lower}
pods = []

cURL = pycurl.Curl()
app = Flask(__name__)

#------------------------TOOLSET-------------------------

@app.route('/cloud/init')
def cloud_init():
    print('Request to initialize cloud')
    # pods = []

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
            pods.append({'name':l_dict['name'], 'id':l_dict['id'], 'isElastic':False, 'upper':None, 'lower':None})
    
    buffer = bytearray()
    print('Initializing medium pod')
    cURL.setopt(cURL.URL, medium_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict1 = json.loads(buffer.decode())
        l_response1 = l_dict1['response']
        if l_response1 != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing medium pod'})
        else:
            pods.append({'name':l_dict1['name'], 'id':l_dict1['id'], 'isElastic':False, 'upper':None, 'lower':None})

    buffer = bytearray()
    print('Initializing heavy pod')
    cURL.setopt(cURL.URL, heavy_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict2 = json.loads(buffer.decode())
        l_response2 = l_dict2['response']
        if l_response2 != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing heavy pod'})
        else:
            pods.append({'name':l_dict2['name'], 'id':l_dict2['id'], 'isElastic':False, 'upper':None, 'lower':None})
            
    return jsonify({'response': 'success', 'pods':pods}) 

@app.route('/cloud/node/register/<name>/<pod_id>')
def register_node(name, pod_id):
    print('Request to register new node: ' + str(name) + ' in pod ' + str(pod_id))
    found = False
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id:
            pod_name = pod['name']
            if pod['isElastic'] == true:
                return jsonify({'response': 'failure',
                                'reason': 'pos is in elastic mode'})
            found = True
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})
    if pod_name == 'light_pod':
        cURL.setopt(cURL.URL,  light_proxy + '/cloudproxy/node/register/' + name + '/' + pod_name)
    elif pod_name == 'medium_pod':
        cURL.setopt(cURL.URL,  medium_proxy + '/cloudproxy/node/register/' + name + '/' + pod_name)
    elif pod_name == 'heavy_pod':
        cURL.setopt(cURL.URL,  heavy_proxy + '/cloudproxy/node/register/' + name + '/' + pod_name)
    buffer = bytearray()
    
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            pod_name = response_dictionary['pod_name']
            name = response_dictionary['name']
            node_status = response_dictionary['node_status']
            return jsonify({'response': 'success',
                            #'port': port,
                            'name': name,
                            'node_status': node_status})
        else:
            result = response_dictionary['result']
            node_status = response_dictionary['node_status']
            return jsonify({'response': 'failure',
                    'reason': 'proxy failure',
                    'proxy_result': result,
                    'node_status':node_status})
    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/cloud/node/remove/<name>/<pod_id>')
def remove_node(name, pod_id):
    print('Request to remove node: ' + str(name) + ' from pod ' + str(pod_id))
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
        cURL.setopt(cURL.URL,  light_proxy + '/cloudproxy/node/remove/' + name + '/' + pod_name)
        server_type = "light-servers"
    elif pod_name == 'medium_pod':
        cURL.setopt(cURL.URL,  medium_proxy + '/cloudproxy/node/remove/' + name + '/' + pod_name)
        server_type = "medium-servers"
    elif pod_name == 'heavy_pod':
        cURL.setopt(cURL.URL,  heavy_proxy + '/cloudproxy/node/remove/' + name + '/' + pod_name)
        server_type = "heavy-servers"
    buffer = bytearray()
    
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        print("200")
        if response == 'success':
            name = response_dictionary['name']
            node_status = response_dictionary['node_status']
            print("success")
            if node_status == 'Removed':
                disable_command = "echo 'experimental-mode on; set server " + server_type +"/"+ name + " state maint' | sudo socat stdio /run/haproxy/admin.sock" 
                subprocess.run(disable_command, shell=True, check=True)
                print("removed")
                command = "echo 'experimental-mode on; del server " + server_type +"/"+ name + "' | sudo socat stdio /run/haproxy/admin.sock" 
                subprocess.run(command, shell=True, check=True)
                return jsonify({'response': 'success',
                                'name': name,
                                'node_status': node_status})
    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/cloud/pod/launch/<pod_id>')
def launch(pod_id):
    print('Request to launch pod: '  + str(pod_id))
    pod_name = ""
    for pod in pods:
        if pod['id'] == pod_id: 
            pod_name = pod['name']
            if pod['isElastic'] == true:
                return jsonify({'response': 'failure',
                                'reason': 'pos is in elastic mode'})
    
    if pod_name == "light_pod":
        pod_URL = light_proxy
        server_type = "light-servers"
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
        server_type = "medium-servers"
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy
        server_type = "heavy-servers"
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})

    cURL.setopt(cURL.URL, pod_URL + '/cloudproxy/pod/launch')
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
            print('port: ' + str(port))
            
            print(pod_URL[7:-5] + ":" + str(port))
            if online:
                command1 = "echo 'experimental-mode on; add server " + server_type +"/"+ name + " " + pod_URL[7:-5] + ":" + str(port) + "' | sudo socat stdio /run/haproxy/admin.sock"
                subprocess.run(command1, shell=True, check=True)
                
                command2 = "echo 'experimental-mode on; set server " + server_type +"/"+ name + " state ready' | sudo socat stdio /run/haproxy/admin.sock"
                subprocess.run(command2, shell=True, check=True) 
                return jsonify({'response': 'success',
                                'port': port,
                                'name': name,
                                'online': online})
    
    return jsonify({'response': 'failure',
                    'reason': 'Unknown'})

@app.route('/cloud/pods/resume/<pod_id>')
def cloud_resume(pod_id):
    print('Request to resume pod: '  + str(pod_id))
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
        server_type = "light-servers"
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
        server_type = "medium-servers"
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy
        server_type = "heavy-servers"

    # get the nodes associated with the pod
    response = requests.get(pod_URL + '/cloudproxy/nodes')
    response_json = response.json()
    if len(response_json) == 0:
        return jsonify({'response': 'failure',
                        'reason': 'no nodes available in pod: ' + pod_name})
    
    for node in response_json:
        if node['status'] == "Online":
            command = "echo 'experimental-mode on; set server " + server_type +"/"+ node['node_name'] + " state ready' | sudo socat stdio /run/haproxy/admin.sock" 
            subprocess.run(command, shell=True, check=True)
    
    return jsonify({'response': 'success',
                    'reason': 'successfully resumed pod ' + pod_name}) 
         
@app.route('/cloud/pods/pause/<pod_id>')
def cloud_pause(pod_id):
    print('Request to pause pod: '  + str(pod_id))
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
        server_type = "light-servers"
    elif pod_name == "medium_pod":
        pod_URL = medium_proxy
        server_type = "medium-servers"
    elif pod_name == "heavy_pod":
        pod_URL = heavy_proxy
        server_type = "heavy-servers"
    
    # get the nodes associated with the pod
    response = requests.get(pod_URL + '/cloudproxy/nodes')
    response_json = response.json()
    if len(response_json) == 0:
        return jsonify({'response': 'failure',
                        'reason': 'no nodes available in pod: ' + pod_name})

    # remove the nodes that are online     
    for node in response_json:
        if node['status'] == "Online":
            # disable the servers
            command = "echo 'experimental-mode on; set server " + server_type +"/"+ node['node_name'] + " state maint' | sudo socat stdio /run/haproxy/admin.sock" 
            subprocess.run(command, shell=True, check=True)
    
    return jsonify({'response': 'success',
                    'reason': 'successfully paused pod ' + pod_name}) 
        


#------------------------TOOLSET-------------------------

#------------------------MONITORING-------------------------

@app.route('/cloud/pods/all')
def cloud_pod_ls():
    print('Request to list all pods')
    return jsonify(pods)

#------------------------MONITORING-------------------------

#------------------------ELASTICITY-------------------------

#TODO
@app.route('/cloud/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower():
    pass

@app.route('/cloud/elasticity/upper/<pod_name>/<value>')
def cloud_elasticity_upper(pod_name, value):
    found = False
    for pod in pods:
        if pod['name'] == pod_name:
            found = True
            # 1. check if elasticity enabled
            if pod['isElastic']:
                # 2. set threshold value in pods list
                pod['upper'] = value
            else:
                return jsonify({'response': 'failure',
                                'reason': 'elasticity is not enabled for pod: ' + str(pod_name)})
    if found == False:
        return jsonify({'response': 'failure',
                        'reason': 'pod not found'})

    # 3. tell EM new threshold +  to adjust nodes to fit threshold
    cURL.setopt(cURL.URL, 'http://10.140.17.108:5000/cloudelastic/elasticity/upper/' + str(pod_name) + '/' + str(value))
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            return jsonify({'response': 'success',
                    'reason': 'upper threshold set to: ' + str(value)}) 
    
    return jsonify({'response': 'failure',
                    'reason': 'Unknown'})

@app.route('/cloud/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable(pod_name, lower, upper):
    print('Request to enable elasticity for pod: '  + str(pod_name))
    found = false
    for pod in pods:
        if pod['name'] == pod_name: 
            found = true
            if pod_name == "light_pod":
                pod_URL = light_proxy
                server_type = "light-servers"
            elif pod_name == "medium_pod":
                pod_URL = medium_proxy
                server_type = "medium-servers"
            elif pod_name == "heavy_pod":
                pod_URL = heavy_proxy
                server_type = "heavy-servers"
            # get the nodes associated with the pod
            response = requests.get(pod_URL + '/cloudproxy/nodes')
            nodes = response.json()
            counter = 0
            for node in nodes:
                if node['status'] == 'Online':
                    counter += 1
                    if counter > upper:
                        remove_node(pod_name, node['node_id'])
            while(counter < lower):
                name = 'node_' + str(counter)
                register_node(name, node['node_id'])
                counter += 1
            cURL.setopt(cURL.URL,  pod_URL + '/cloudelastic/elasticity/enable/' + pod_name + '/' + str(lower) + '/' + str(upper))
            buffer = bytearray()
            cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
            cURL.perform()
    
            if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
                response_dictionary = json.loads(buffer.decode())
                response = response_dictionary['response']
                if response == 'success':
                    pod['isElastic'] = true 
                    return jsonify({'response': 'success',
                                    'reason': 'successfully enabled elasticity for pod ' + pod_name})
                else:
                    return jsonify({'response': 'failure',
                                    'reason': 'elastic manager failure'})    
            if found == False:
                return jsonify({'response': 'failure',
                                'reason': 'pod not found'})
     return jsonify({'response': 'failure',
                    'reason': 'unknown'})
   

@app.route('/cloud/elasticity/disable/<pod_name>')
def cloud_elasticity_disable(pod_name):
    print('Request to disable elasticity for pod: '  + str(pod_name))
    for pod in pods:
        if pod['name'] == pod_name:
            pod['isElastic'] = flase
            return jsonify({'response': 'success',
                    'reason': 'successfully disabled elasticity for pod ' + pod_name})
    return jsonify({'response': 'failure',
                        'reason': 'pod not found'})

#------------------------ELASTICITY-------------------------

#------------------------UNSUPPORTED-------------------------

@app.route('/cloud/pod/register/<name>')
def cloud_pod(name):
    print('Request to register new pod: ' + str(name))
    result = 'The current cloud system cannot register new pods'
    return jsonify({'result': result})

@app.route('/cloud/pod/rm/<name>')
def cloud_pod_rm(name):
    print('Request to register new pod: ' + str(name))
    result = 'The current cloud system does not allow users to remove pods'
    return jsonify({'result': result})

#------------------------UNSUPPORTED-------------------------

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5000)
