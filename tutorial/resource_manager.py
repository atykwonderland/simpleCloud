from flask import Flask, jsonify, request 
import sys 
import pycurl 
import json 
import subprocess

ip_proxy = 'http://10.140.17.107:5001'
ip_proxy_no_port = '10.140.17.107'

cURL = pycurl.Curl()
app = Flask(__name__)

@app.route ('/remove/<name>')
def remove_node(name):
    print("About to get on:" + ip_proxy + '/rm/' + name)
    cURL.setopt(cURL.URL, ip_proxy + '/rm/' + name)
    buffer = bytearray()

    cURL.setopt (cURL.WRITEFUNCTION, buffer.extend)

    cURL.perform()
    print(cURL.getinfo(cURL.RESPONSE_CODE)) 
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            port = response_dictionary['port']
            name = response_dictionary['name']
            running = response_dictionary['running']
            if running:
                disable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state maint ' + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(disable_command, shell=True, check=True)
                
                command = "echo 'experimental-mode on; del server light-servers/'" + name + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(command, shell=True, check=True)

            return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running})
    
    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/register/<name>/<port>')
def register_node (name, port):
    cURL.setopt (cURL.URL, ip_proxy + '/register/' + name + '/' + port)
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()
    
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            port = response_dictionary['port']
            name = response_dictionary['name']
            running = response_dictionary['running']
            return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running})

    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

@app.route('/launch')
def launch():
    cURL.setopt(cURL.URL, ip_proxy + '/launch')
    buffer = bytearray()

    cURL.setopt (cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        response_dictionary = json.loads(buffer.decode())
        response_dictionary = json.loads(buffer.decode())
        response = response_dictionary['response']
        if response == 'success':
            port = response_dictionary['port']
            name = response_dictionary['name']
            running = response_dictionary['running']
            print('port: ' + port)
            if running:
                command = "echo 'experimental-mode on; add server light-servers/'" + name + ' ' + ip_proxy_no_port + ':' + port + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(command, shell=True, check=True)
                
                enable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state ready ' + '| sudo socat stdio /run/haproxy/admin.sock'
                subprocess.run(enable_command, shell=True, check=True) 
                return jsonify({'response': 'success',
                                'port': port,
                                'name': name,
                                'running': running})
    
    return jsonify({'response': 'failure',
                    'reason': 'Unknown'})

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6001)