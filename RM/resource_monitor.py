from flask import Flask, request
import requests

proxy_url = 'http://winter2023-comp598-group03-01.cs.mcgill.ca:6000'
app = Flask(__name__)

@app.route('/cloudmonitor/pods/all', methods=['GET'])
def cloud_pod_ls():
    if request.method == 'GET':
        print('Request to list all pods')
        response = requests.get(proxy_url + '/cloudproxy/pods/all')
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/nodes/all', methods=['GET'])
def cloud_node_ls_all():
    if request.method == 'GET':
        print('Request to list all nodes')
        response = requests.get(proxy_url + '/cloudproxy/nodes/all')
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/nodes/<pod_id>', methods=['GET'])
def cloud_node_ls(pod_id):
    if request.method == 'GET':
        print('Request to list all nodes in pod ' + pod_id)
        response = requests.get(proxy_url + '/cloudproxy/nodes/' + pod_id)
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/jobs/all', methods=['GET'])
def cloud_job_ls_all():
    if request.method == 'GET':
        print('Request to list all jobs')
        response = requests.get(proxy_url + '/cloudproxy/jobs/all')
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/jobs/<node_id>', methods=['GET'])
def cloud_job_ls(node_id):
    if request.method == 'GET':
        print('Request to list all jobs in node ' + node_id)
        response = requests.get(proxy_url + '/cloudproxy/jobs/' + node_id)
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/jobs/log/<job_id>', methods=['GET'])
def cloud_job_log(job_id):
    if request.method == 'GET':
        print('Request to list logs for job ' + job_id)
        response = requests.get(proxy_url + '/cloudproxy/jobs/log/' + job_id)
        response_json = response.json()
        return response_json

@app.route('/cloudmonitor/nodes/log/<node_id>', methods=['GET'])
def cloud_log_node(node_id):
    if request.method == 'GET':
        print('Request to list all logs in node ' + node_id)
        response = requests.get(proxy_url + '/cloudproxy/nodes/log/' + node_id)
        response_json = response.json()
        return response_json

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)