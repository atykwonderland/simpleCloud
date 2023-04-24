from flask import Flask, render_template
import requests
import json

monitor_url = 'http://winter2023-comp598-group03-02.cs.mcgill.ca:7000'
app = Flask(__name__, template_folder='templates')

@app.route('/cloudmonitor/dashboard/')
def cloud_dashboard():

    # display style:
    # node_name | node_status | node_log
    response = requests.get(monitor_url + '/cloudmonitor/nodes/all')
    response_json = response.json()
    nodes = []
    for data in response_json:
        d = {}
        for key, value in data.items():
            d[key] = value
            print (key, value)
        nodes.append(d)

    logs = []
    for node in nodes:
        response = requests.get(monitor_url + '/cloudmonitor/nodes/log/' + node['node_id'])
        response_json = response.json()
        log = json.dumps(response_json)
        logs.append(log)

    nodes_with_logs = zip(nodes, logs)

    #return render_template("index.html", nodes = nodes, logs = logs)
    return render_template("index.html", nodes_with_logs = nodes_with_logs)

if __name__ == '__main__':
    app.run(use_reloader = True, debug=True, host='0.0.0.0', port=3000)