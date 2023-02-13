from flask import Flask, jsonify, request
import time
import docker
import proxy.py as proxy

def job_dispatch():
    while 1:
        job = proxy.job_queue[0]
        if job.status == "Registered":
            for node in proxy.nodes:
                try:
                    container = proxy.client.containers.get(node.name)
                    job.status = "Running"
                    node.status = "Running"
                    job.node_id = node.id
                    commands = job.file.realines()
                    command_str = commands[0].decode("ascii")
                    for i, command in enumerate(commands):
                        if i > 0:
                            command_str = command_str[:(len(command_str)-1)] + ";" + command.decode("ascii")
                    (exec_code, output) = container.exec_run(command_str)
                    node.jobs_output.append(str({'job_id' : job.id, 'output' : output}))
                    job.status = "Completed"
                    node.status = "Idle"
                    result = 'Job' + str(job.id) + ' is completed'
                    return jsonify({'result' : result})
                except docker.errors.NotFound:
                    continue
            time.sleep(5)
        else:
            proxy.job_queue.remove[0]
            continue
