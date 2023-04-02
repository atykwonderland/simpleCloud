from flask import Flask, jsonify, request 
import requests
import pycurl 
import json 
import subprocess
from io import BytesIO
import datetime

light_proxy = 'http://10.140.17.109:6001'
medium_proxy = 'http://10.140.17.109:6002'
heavy_proxy = 'http://10.140.17.109:6003'

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
def cloud_elasticity_enable():
    pass

@app.route('/cloudelastic/elasticity/lower/<pod_name>')
def cloud_elasticity_disable():
    pass

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5002)
