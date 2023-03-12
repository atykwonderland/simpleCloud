from flask import Flask, jsonify, request 
import sys 
import pycurl 
import json 
import subprocess
from io import BytesIO
import requests

light_proxy = 'http://10.140.17.108:5001'
light_proxy_no_port = '10.140.17.108'

medium_proxy = 'http://10.140.17.107:5001'
medium_proxy_no_port = '10.140.17.107'

heavy_proxy = 'http://10.140.17.109:5001'
heavy_proxy_no_port = '10.140.17.109'

pods = []

cURL = pycurl.Curl()
app = Flask(__name__)

#------------------------TOOLSET-------------------------

@app.route('/cloud/init', methods=['GET'])
def cloud_init():
    print('Request to initialize cloud')
    buffer = bytearray()

    print('Initializing light pod')
    cURL.setopt(cURL.URL, light_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing light pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})

    print('Initializing medium pod')
    cURL.setopt(cURL.URL, medium_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing medium pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})

    print('Initializing heavy pod')
    cURL.setopt(cURL.URL, heavy_proxy + '/cloudproxy/init')
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        l_dict = json.loads(buffer.decode())
        l_response = l_dict['response']
        if l_response != 'success':
            return jsonify({'response': 'failure',
                            'reason': 'error while initializing heavy pod'})
        else:
            pods.append({'name':l_dict['name'], 'id':l_dict['id']})
            
    return jsonify({'response': 'success'}) 

#------------------------TOOLSET-------------------------

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=6001)