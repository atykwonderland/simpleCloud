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
processes = {
    'light_pod': None
    'medium_pod': None
    'heavy_pod': None
}

cURL = pycurl.Curl()
app = Flask(__name__)

#TODO
@app.route('/cloudelastic/elasticity/lower/<pod_name>/<value>')
def cloud_elasticity_lower():
    pass

@app.route('/cloudelastic/elasticity/upper/<pod_name>/<value>')
def cloud_elasticity_upper(pod_name, value):
    # set threshold value for pod
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        thresholds[pod_name]['upper'] = value
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
    
    # trigger thread to refresh?

    return jsonify({'response': 'success',
                    'result': 'upper threshold set to: ' + str(value)})

def light_pod_task():
    while(true):
        manage_light()
        time.sleep(5)
        
def medium_pod_task():
    while(true):
        manage_medium()
        time.sleep(5)
        
def heavy_pod_task():
    while(true):
        manage_heavy()
        time.sleep(5)
        
@app.route('/cloudelastic/elasticity/enable/<pod_name>/<lower>/<upper>')
def cloud_elasticity_enable(pod_name, lower, upper):
    if pod_name == "light_pod":
        pod_limits['light_pod']['upper'] = upper
        pod_limits['light_pod']['lower'] = lower
        task = Process(target=light_pod_task)
        processes['light_pod'] = task
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    elif pod_name == "medium_pod":
        pod_limits['medium_pod']['upper'] = upper
        pod_limits['medium_pod']['lower'] = lower
        task = Process(target=medium_pod_task)
        processes['medium_pod'] = task
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    elif pod_name == "heavy_pod":
        pod_limits['heavy_pod']['upper'] = upper
        pod_limits['heavy_pod']['lower'] = lower
        task = Process(target=heavy_pod_task)
        processes['heavy_pod'] = task
        task.start()
        return jsonify({'response': 'success',
                        'reason': 'elastic manager enabled for pod' + pod_name})
    else:
        return jsonify({'response': 'failure',
                        'reason': 'unknown pod'})
   

@app.route('/cloudelastic/elasticity/disable/<pod_name>')
def cloud_elasticity_disable(pod_name):
    print('Request to disable elasticity for pod: '  + str(pod_name))
    if pod_name == "light_pod" or pod_name == "medium_pod" or pod_name == "heavy_pod":
        process = processes[pod_name]
        process.kill()
        return jsonify({'response': 'success',
                        'reason': 'successfully disabled elasticity for pod ' + pod_name})
    return jsonify({'response': 'failure',
                    'reason': 'pod not found'})

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5002)
