from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/cloudmonitor/pods/all')
def cloud_get_all_pods():
    if request.method == 'GET':
        #TODO: loop through all pods and add them to the json
        pass

@app.route('/cloudmonitor/nodes/all')
def cloud_get_all_nodes():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        pass

@app.route('/cloudmonitor/jobs/all')
def cloud_get_all_jobs():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        pass

@app.route('/cloudmonitor/jobs/log/<job_id>')
def cloud_get_job_log():
    if request.method == 'GET':
        #TODO: get log for job_id
        pass

@app.route('/cloudmonitor/nodes/log/<node_id>')
def cloud_get_job_log():
    if request.method == 'GET':
        #TODO: get log for node_id
        pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)