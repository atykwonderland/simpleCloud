# COMP598
## Group 3:
Alice Kang 260827823

Hana Zhang 260887780

Joshua Roccamo 260669999

---

## Files to start when starting the cloud:

On comp598-user@winter2023-comp598-group03-02:
* resource_manager.py
* resource_monitor.py
* cloud_dashboard.py
* light_proxy.py

On comp598-user@winter2023-comp598-group03-01:
* cloud_toolset.py
* medium_proxy.py

On comp598-user@winter2023-comp598-group03-03:
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
