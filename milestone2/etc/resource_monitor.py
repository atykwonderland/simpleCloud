from flask import Flask, jsonify
import json
import requests
import datetime
import pandas as pd
import subprocess

light_proxy = 'http://10.140.17.108:6001'
medium_proxy = 'http://10.140.17.107:6001'
heavy_proxy = 'http://10.140.17.109:6001'
manager = 'http://10.140.17.108:6002'

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
        print(response_json)
        return response_json
    elif pod_name == 'medium_pod':
        response = requests.get(medium_proxy + '/cloudproxy/nodes')
        response_json = response.json()
        return response_json
    elif pod_name == 'heavy_pod':
        response = requests.get(heavy_proxy + '/cloudproxy/nodes')
        response_json = response.json()
        return response_json
    
    return response_json

#------------------------HAPROXY LOGGING-------------------------

@app.route('/cloudmonitor/logs')
def cloud_log_request():
    print('Request to get all end user requests')

    command = 'echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d "," -f 1-2,18,47-48,59-61,74,77 > logs/haproxy.log'
    subprocess.run(command, shell=True, check=True)

    logs_df = pd.read_csv('logs/haproxy.log', sep=',')

    result = logs_df.to_json(orient="records")
    parsed = json.loads(result)
    
    return parsed

@app.route('/cloudmonitor/logs/<pod_name>')
def cloud_log_pod(pod_name):
    print('Request to list all incoming end user requests in pod ' + pod_name)

    if pod_name == "light_pod":
        command = 'echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d "," -f 1-2,18,47-48,59-61,74,77 | grep -e pxname -e light-servers > logs/light.log'
        subprocess.run(command, shell=True, check=True)
        logs_df = pd.read_csv('logs/light.log', sep=',')
    elif pod_name == "medium_pod":
        command = 'echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d "," -f 1-2,18,47-48,59-61,74,77 | grep -e pxname -e medium-servers > logs/medium.log'
        subprocess.run(command, shell=True, check=True)
        logs_df = pd.read_csv('logs/medium.log', sep=',')
    elif pod_name == "heavy_pod":
        command = 'echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d "," -f 1-2,18,47-48,59-61,74,77 | grep -e pxname -e heavy-servers > logs/heavy.log'
        subprocess.run(command, shell=True, check=True)
        logs_df = pd.read_csv('logs/heavy.log', sep=',')
    else:
        return jsonify({'response':'failure', 'result':'invalid pod name'})

    result = logs_df.to_json(orient="records")
    parsed = json.loads(result)
    
    return parsed

#------------------------HAPROXY LOGGING-------------------------
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6003)