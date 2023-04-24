from flask import Flask, render_template
import requests
import json

monitor_url = 'http://10.140.17.108:6003'
app = Flask(__name__, template_folder='templates')

@app.route('/cloudmonitor/dashboard')
def cloud_dashboard():
    # shows a live representation of the incoming requests for each pod.
    response = requests.get(monitor_url + '/cloudmonitor/logs')
    logs = response.json()

    response = requests.get(monitor_url + '/cloudmonitor/resource_utilization')
    usage = response.json()

    return render_template("index.html", logs = logs, usage = usage)

if __name__ == '__main__':
    app.run(use_reloader = True, debug=True, host='0.0.0.0', port=3000)