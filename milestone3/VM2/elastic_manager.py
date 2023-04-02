from flask import Flask, jsonify, request 
import requests
import pycurl 
import json 
import subprocess
from io import BytesIO
import datetime
from multiprocessing import Process

light_proxy = 'http://10.140.17.109:6001'
medium_proxy = 'http://10.140.17.109:6002'
heavy_proxy = 'http://10.140.17.109:6003'

thresholds = {
    'light_pod': {'upper':None, 'lower':None},
    'medium_pod': {'upper':None, 'lower':None},
    'heavy_pod': {'upper':None, 'lower':None}
}
pod_limits = {
    'light_pod': {'upper':None, 'lower':None},
    'medium_pod': {'upper':None, 'lower':None},
    'heavy_pod': {'upper':None, 'lower':None}
}

cURL = pycurl.Curl()
app = Flask(__name__)

#TODO
@app.route('/cloudelastic/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower():
    pass

@app.route('/cloudelastic/elasticity/upper/<pod_name>/<value>')
def cloud_elasticity_upper():
    pass

@app.route('/cloudelastic/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable(pod_name, lower, upper):
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        pod_limits[pod_name]['upper'] = upper
        pod_limits[pod_name]['lower'] = lower
        pod_task = pod_name + '_task'
        pod['isElastic'] == true:
        task = Process(target=pod_task, args=(thresholds[pod_name]['lower'], thresholds[pod_name]['upper']))
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
   

@app.route('/cloudelastic/elasticity/disable/<pod_name>')
def cloud_elasticity_disable(pod_name):
    print('Request to disable elasticity for pod: '  + str(pod_name))
    for pod in pods:
        if pod['name'] == pod_name:
            pod['isElastic'] = flase
            return jsonify({'response': 'success',
                    'reason': 'successfully disabled elasticity for pod ' + pod_name})
    return jsonify({'response': 'failure',
                        'reason': 'pod not found'})

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5002)
