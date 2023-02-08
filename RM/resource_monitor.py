from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/cloudmonitor/pods/all')
def cloudmonitor_get_all_pods():
    # TODO: loop through all pods and add them to the json
    if request.method == 'GET':
        response = requests.get('/cloudproxy/pods/all')
        for pod in response:
            print("pod name: "+pod.name)
            print("pod id: " + pod.id)
            print("number of jobs: "+requests.get('/cloudproxy/pods/job_numbers'))
        return response


@app.route('/cloudmonitor/nodes/all')
def cloudmonitor_get_all_nodes():
    if request.method == 'GET':
        #TODO: loop through all nodes and add them to the json

        nodes = requests.get('cloudproxy/nodes/all')
        for node in nodes:
            print("name: "+node.name)
            print("id: " + node.id)
            print("status: " + node.status)

        return nodes


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

        job = requests.get('/cloudproxy/jobs/'+str(node_id))

        print("job path: " + job.path)
        print("job ID: " + job.id)
        print("job status: " + job.status)

        return job


@app.route('/cloudmonitor/jobs/log/<job_id>')
def cloudmonitor_get_job_log(node_id, job_id):
    if request.method == 'GET':
        #TODO: get log for job_id
        log = cloudmonitor_get_node_log(node_id)
        return jsonify(log[job_id])



@app.route('/cloudmonitor/nodes/log/<node_id>')
def cloudmonitor_get_node_log(node_id):
    if request.method == 'GET':
        #TODO: get log for node_id
        response = requests.get("/cloudproxy/nodes/log/" + str(node_id))
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)


