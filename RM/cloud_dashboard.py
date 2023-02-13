from flask import Flask, render_template
import requests
import json

monitor_url = 'http://winter2023-comp598-group03-02.cs.mcgill.ca:7000'
app = Flask(__name__)

@app.route('/cloudmonitor/dashboard/')
def cloud_dashboard():

    # display style:
    # node_name | node_status | node_log
    response = requests.get(monitor_url + '/cloudproxy/nodes/all')
    response_json = response.json()
    nodes = json.loads(response_json)

    return render_template("index.html", nodes = nodes)

if __name__ == '__main__':
    app.run(use_reloader = True, debug=True, host='0.0.0.0', port=8000)