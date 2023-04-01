from flask import Flask, render_template
import requests
import json

monitor_url = 'http://winter2023-comp598-group03-02.cs.mcgill.ca:7000'
app = Flask(__name__, template_folder='templates')

@app.route('/cloudmonitor/dashboard/')
def cloud_dashboard():
    # shows a live representation of the incoming requests for each pod.
    # pod_name || timestamp | request
    response = requests.get(monitor_url + '/cloudmonitor/pods/all')
    response_json = response.json()
    pods = []
    for data in response_json:
        d = {}
        for key, value in data.items():
            d[key] = value
            print (key, value)
        pods.append(d)

    requests = []
    for pod in pods:
        response = requests.get(monitor_url + '/cloudmonitor/pods/requests/' + pod['pod_name'])
        response_json = response.json()
        req = json.dumps(response_json)
        requests.append(req)

    pods_with_reqs = zip(pods, requests)

    return render_template("index.html", pods_with_reqs = pods_with_reqs)

if __name__ == '__main__':
    app.run(use_reloader = True, debug=True, host='0.0.0.0', port=3000)