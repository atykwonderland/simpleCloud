# COMP598 - McGill
## Simple Elastic Cloud with Load Balancer
A basic cloud management system that will manage and monitor a cluster of machines and use them to run jobs.
Nodes and Pods are depicted by docker containers and networks, respectively. 

## Group 3:
Alice Kang,
Hana Zhang,
Joshua Roccamo

---

## Dependencies:
* docker
* haproxy
* nginx
* ...

---

## Files to start when starting the cloud:

On comp598-user@winter2023-comp598-group03-02:
* resource_manager.py
* resource_monitor.py
* cloud_dashboard.py
* elastic_manager.py
* request_load.py <- for testing different loads on the elastic manager

On comp598-user@winter2023-comp598-group03-01:
* cloud_toolset.py

On comp598-user@winter2023-comp598-group03-03:
* light_proxy.py
* medium_proxy.py
* heavy_proxy.py

---

## After running the above files:
* use the cloud_toolset commands to run the toolset (node/pod management) and monitoring commands
* access the cloud dashboard by opening this link in a web browser: http://127.0.0.1:3000/cloudmonitor/dashboard
* to see the stats live without going to the dashboard: `watch 'echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d "," -f 1-2,18,47-48,59-61,74,77 | column -s, -t'`

---

## Supported Toolset Commands

```
cloud init
cloud pod register {pod_name}
cloud pod rm {pod_name}
cloud register {node_name} {pod_id}
cloud rm {node_name} {pod_id}
cloud launch {pod_id}
cloud resume {pod_id}
cloud pause {pod_id}
cloud elasticity lower_threshold {pod_name} {value}
cloud elasticity upper_threshold {pod_name} {value}
cloud elasticity enable {pod_name} {lower_size} {upper_size}
cloud elasticity disable {pod_name}
```

---

## Supported Monitoring Commands

```
cloud pod ls
cloud node ls {pod_id}
cloud log request
cloud log pod {pod_name}
```

---

## Supported End User Requests

```
curl http://10.140.17.108:5001/light/app
curl http://10.140.17.108:5002/medium/app
curl http://10.140.17.108:5003/heavy/app
```
