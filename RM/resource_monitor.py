from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/cloudmonitor/pods/all')
def cloudmonitor_get_all_pods():
    # TODO: loop through all pods and add them to the json
    if request.method == 'GET':
        pods = client.networks.list()
        response = requests.get('/cloud/pods/'+pods[0]).json()
        for pod in pods[1:]:
            response.update(requests.get('/cloud/pods/'+str(pod)).json())
        return response


@app.route('/cloudmonitor/nodes/all')
def cloudmonitor_get_all_nodes():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        return requests.get('cloudproxy/nodes/all')


@app.route('/cloudmonitor/jobs/all')
def cloudmonitor_get_all_jobs():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json

        jobs = requests.get('/cloudproxy/jobs/all')

        for job in jobs:
            print("job path: "+ job.path)
            print("job ID: " + job.id)
            print("job status: " + job.status)

        return jobs

@app.route('/cloudmonitor/jobs/<node_id>')
def cloudmonitor_get_job(node_id):
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json
        response = requests.get('/cloudproxy/jobs/<node_id>')
        return response


@app.route('/cloudmonitor/jobs/log/<job_id>')
def cloudmonitor_get_job_log(node_id, job_id):
    if request.method == 'GET':
        #TODO: get log for job_id
        response = requests.get("/cloudproxy/logs/"+str(node_id)+"/"+str(job_id))
        return jsonify(response)


@app.route('/cloudmonitor/nodes/log/<node_id>')
def cloudmonitor_get_node_log(node_id):
    if request.method == 'GET':
        #TODO: get log for node_id
        response = requests.get("/cloudproxy/logs/" + str(node_id))
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)


# # in the cloud proxy:
# @app.route('/cloudproxy/jobs/all')
# def proxy_get_all_jobs():
#     if request.method == 'GET':
#         return jobs             # a list of jobs (global variable in the proxy)
#
# @app.route('/cloudproxy/logs/<node_id>')
# def proxy_get_log_node(node_id):
#     if request.method == 'GET':
#         return logs[node_id]             # a list of logs (global variable in the proxy)
#
# @app.route('/cloudproxy/logs/<node_id>/<job_id>')
# def proxy_get_log_job(node_id, job_id):
#     if request.method == 'GET':
#         return logs[node_id][job_id]             # a list of logs (global variable in the proxy)