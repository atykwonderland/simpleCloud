import docker 
import sys
from flask import Flask, jsonify, request

client = docker.from_env()

app = Flask(__name__)

node_list = []

@app.route('/register/<name>/<port>')
def register(name, port):
    for node in node_list:
        print(node['port'])
        print(port)
        if node['port'] == port:
            return jsonify({'response': 'failure',
                            'reason': 'port already taken'})
        elif node['name'] == name:
            return jsonify({'response': 'failure',
                            'reason': 'name already taken'})

    node_list.append({'port': port, 'name': name, 'running': False})
    print(node_list)
    return jsonify({'response': 'success',
                    'port': port,
                    'name': name,
                    'running': False})

@app.route('/launch')
def launch():
    for node in node_list:
        if not node['running']:
            node = launch_node(node['name'], node['port'])
            if node is not None:
                return jsonify({'response': 'success',
                                'port': node ['port'],
                                'name' : node ['name'],
                                'running': node['running']})

    return jsonify({'response': 'failure',
                    'reason': 'unknown reason'})

@app.route('/rm/<node_name>')
def remove (node_name):
    index_to_remove = -1
    for i in range(len(node_list)):
        node = node_list[i]
        if node['name'] == node_name:
            index_to_remove = i
            break
    found = False
    port = -1
    name = ''
    running = False
    if index_to_remove != -1:
        node = node_list[index_to_remove]
        port = node['port']
        name = node['name']
        running = node['running']
        del node_list[index_to_remove]
        found = True

    for container in client.containers.list():
        if container.name == node_name:
            container.remove(v=True, force=True) 
            break
        found = False
    
    if found:
        return jsonify({'response': 'success',
                        'port': port,
                        'name': name,
                        'running': running})

    return jsonify({'response': 'failure'})

@app.route('/rmall')
def remove_all():
    node_list.clear()
    for container in client.containers.list():
        container.remove(v=True, force=True) 
    print('successfully removed all nodes') 
    return jsonify({'response': 'success'})

def launch_node(container_name, port_number):
    [img, logs] = client.images.build (path='/home/comp598-user/tutorial/', rm=True, dockerfile='/home/comp598-user/tutorial/Dockerfile')
    for container in client.containers.list():
        if container.name == container_name:
            container.remove (v=True, force=True) 
    
    client.containers.run (image=img,
                            detach=True, 
                            name=container_name, 
                            command=['python','app.py', container_name],
                            ports={'5000/tcp': port_number})
    
    index = -1
    for i in range(len(node_list)):
        node = node_list[i]
        if container_name == node ['name']:
            index = i
            node_list[i] = {'port': port_number, 'name': container_name, 'running': True}
            break

    print("Succesfully launched a node")
    return node_list[index]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)