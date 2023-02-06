from flask import Flask, jsonify, request
import pycurl
import json
from io import BytesIO

cURL = pycurl.Curl()
proxy_url = 'http://192.168.124.89:6000' #TODO: change this with our VM addresses

app = Flask(__name__)

@app.route('/', methods=['GET'])
def cloud():
    if request.method == 'GET':
        print('A client says hello')
        response = 'Cloud says hello!'
        return jsonify({'response': response})

#TODO
@app.route('/cloud/init', methods=['GET'])
def cloud_init():
    if request.method == 'GET':
        pass

@app.route('/cloud/pods/<name>', methods=['GET', 'DELETE'])
def cloud_pod():
    #TODO: register new pod with name
    if request.method == 'GET':
        pass
    
    #TODO: delete existing pod with name
    elif request.method == 'DELETE':
        pass

@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'}, methods=['GET', 'DELETE'])
@app.route('/cloud/nodes/<name>/<pod_name>', methods=['GET']) 
def cloud_node(name, pod_name):
    # register node with name
    if request.method == 'GET':
        print('Request to reigster new node: ' + str(name) + ' on pod: ' + str(pod_name))
        #TODO: logic for invoing RM-proxy
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/nodes/', + str(name))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        node_status = dictionary['node_status']
        new_node_name = dictionary['node_name']
        new_node_pod = pod_name
        
        return jsonify({'result': result, 'node_status': node_status, 'new_node_name': str(name), 'new_pod_name':str(pod_name)}) 
    
    #TODO: delete existing node with name
    elif request.method == 'DELETE':
        pass

@app.route('/cloud/jobs/launch', methods=['POST'])
def cloud_launch():
    if request.method == 'POST':
        print('Request to post a file')
        job_file = request.files['files']
        #TODO: send job to appropriate proxy
        print(job_file.read())
        result = 'success'
        return jsonify({'result': result})

#TODO
@app.route('/cloud/jobs/abort/<job_id>', methods=['DELETE'])
def cloud_abort():
    if request.method == 'DELETE':
        pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)