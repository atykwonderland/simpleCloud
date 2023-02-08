from flask import Flask, jsonify, request
import pycurl
import json
from io import BytesIO
import requests

cURL = pycurl.Curl()
proxy_url = 'http://winter2023-comp598-group03-01.cs.mcgill.ca:6000' #TODO: change this with our VM address

app = Flask(__name__)

@app.route('/', methods=['GET'])
def cloud():
    if request.method == 'GET':
        print('A client says hello')
        response = 'Cloud says hello!'
        return jsonify({'response': response})

#------------------------ALICE-------------------------

@app.route('/cloud/init', methods=['GET'])
def cloud_init():
    if request.method == 'GET':
        print('Request to initialize cloud')
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/init')
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        return jsonify({'result': result}) 

@app.route('/cloud/pods/<name>', methods=['GET', 'DELETE'])
def cloud_pod(name):
    if request.method == 'GET':
        print('Request to register a new pod: ' + str(name))
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/pods/' + str(name))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        return jsonify({'result': result, 'pod_name':str(name)}) 
    
    elif request.method == 'DELETE':
        print('Request to remove pod: ' + str(name))
        ret = requests.delete(proxy_url + '/cloudproxy/pods/' + str(name))
        print(ret.text)
        return jsonify({'result': str(ret.result), 'pod_name':str(name)}) 

@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'}, methods=['GET'])
@app.route('/cloud/nodes/<name>/<pod_name>', methods=['GET']) 
def cloud_node(name, pod_name):
    if request.method == 'GET':
        print('Request to reigster new node: ' + str(name) + ' on pod: ' + str(pod_name))
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/nodes/' + str(name))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        node_status = dictionary['node_status']
        new_node_name = dictionary['node_name']
        
        return jsonify({'result': result, 'node_status': node_status, 'new_node_name': new_node_name, 'pod_name':str(pod_name)}) 

@app.route('/cloud/nodes/<name>', methods=['DELETE'])   
def cloud_node_rm(name):
    if request.method == 'DELETE':
        print('Request to remove node: ' + str(name))
        ret = requests.delete(proxy_url + '/cloudproxy/nodes/' + str(name))
        print(ret.text)
        return jsonify({'result': str(ret.result), 'node_name':str(name)}) 


#------------------------HANA-------------------------

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

#-------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)