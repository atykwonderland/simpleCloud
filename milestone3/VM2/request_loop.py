import pycurl
import time
import csv
from io import BytesIO
import json
from datetime import datetime
import multiprocessing


cURL = pycurl.Curl()

def request_loop(iterations, wait_time, ip_proxy):
    for i in range(iterations):
        cURL.setopt(cURL.URL, ip_proxy)
        cURL.perform()
        time.sleep(wait_time)

def main_loop():
    app_urls = {"light_pod": "http://10.140.17.108:5001/light/app", "medium_pod": "http://10.140.17.108:5002/medium/app",
                "heavy_pod": "http://10.140.17.108:5003/heavy/app"}
    iterations = input("Enter the number of iterations: \n")
    delay = input("Enter the delay: \n")
    ip_proxy = input("Enter the proxy: \n")
    while True:
        request_loop(int(iterations), float(delay), app_urls[str(ip_proxy)])

if __name__ == '__main__':
    main_loop()


