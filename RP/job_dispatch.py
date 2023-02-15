from flask import Flask, jsonify, request
import time
import docker
import proxy.py as proxy

while 1:
    if len(proxy.job_queue) > 0:
        if proxy.job_queue[0].status == "Registered":
            for node in proxy.nodes:
                if node.status == "Idle":
                    try:
                        container = proxy.client.containers.get(node.name)
                        proxy.job_queue[0].status = "Running"
                        for j in proxy.jobs:
                            if j.id == proxy.job_queue[0].id:
                                j.status = "Running"
                                j.node_id = node.id
                        node.status = "Running"
                        proxy.job_queue[0].node_id = node.id
                        commands = proxy.job_queue[0].file.realines()
                        command_str = commands[0].decode("ascii")
                        for i, command in enumerate(commands):
                            if i > 0:
                                command_str = command_str[:(len(command_str)-1)] + ";" + command.decode("ascii")
                        (exec_code, output) = container.exec_run(command_str)
                        node.jobs_output.append(str({'job_id' : proxy.job_queue[0].id, 'output' : output}))
                        for j in proxy.jobs:
                            if j.id == proxy.job_queue[0].id:
                                j.status = "Completed"
                        proxy.job_queue[0].status = "Completed"
                        node.status = "Idle"
                        result = 'Job' + str(proxy.job_queue[0].id) + ' is completed'
                        print(result)
                    except docker.errors.NotFound:
                        continue
            time.sleep(5)
        else:
            proxy.job_queue.remove[0]
            continue
    else:
        time.sleep(5)
