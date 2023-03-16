from flask import Flask
import requests

light_proxy = 'http://10.140.17.108:5001'
medium_proxy = 'http://10.140.17.107:5001'
heavy_proxy = 'http://10.140.17.109:5001'
manager = 'http://winter2023-comp598-group03-02.cs.mcgill.ca:6001'

app = Flask(__name__)

@app.route('/cloudmonitor/pods/all')
def cloud_pod_ls():
    print('Request to list all pods')
    response = requests.get(manager + '/cloud/pods/all')
    response_json = response.json()
    return response_json

@app.route('/cloudmonitor/nodes/<pod_name>')
def cloud_node_ls(pod_name):
    print('Request to list all nodes in pod ' + pod_name)
    response_json = {}

    if pod_name == 'light_pod':
        response = requests.get(light_proxy + '/cloudproxy/nodes')
        response_json = response.json()
        return response_json
    elif pod_name == 'medium_pod':
        response = requests.get(light_proxy + '/cloudproxy/nodes')
        response_json = response.json()
        return response_json
    elif pod_name == 'heavy_pod':
        response = requests.get(light_proxy + '/cloudproxy/nodes')
        response_json = response.json()
        return response_json
    
    return response_json

@app.route('/cloudmonitor/pods/requests/<pod_name>')
def cloud_log_node(pod_name):
    print('Request to list all incoming requests in pod ' + pod_name)
    response = requests.get(manager + '/cloud/pod/requests/' + pod_name)
    response_json = response.json()
    return response_json
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)