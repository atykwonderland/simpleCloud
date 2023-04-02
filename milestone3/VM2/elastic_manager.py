#TODO


# def compute_usage(pod_name):

#     buffer = bytearray()
#     cURL.setopt(cURL.URL, pod_name + '/cloudproxy/compute_usage')
#     cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
#     cURL.perform()
#     cpu_usage = json.loads(buffer.decode())
#     cpu_usage = usage['response']
#     return cpu_usage

# @app.route('/elastic_manager/elasticity/lower/<pod_name>/<value>')
# def cloud_elasticity_lower(name, value):

#     cpu_usage = compute_usage(pod_name)        
#     # remove a node by setting it to "NEW"
#     while cpu_usage < value:
#         for node in response_json:
#             if node['status'] == "Online" and cpu_usage < value:
#                 command = "echo 'experimental-mode on; set server " + server_type +"/"+ node['node_name'] + " state maint' | sudo socat stdio /run/haproxy/admin.sock" 
#                 subprocess.run(command, shell=True, check=True)
#                 node['status'] == "NEW"
#             cpu_usage = compute_usage()   # re-compute the usage, since it will have changed
