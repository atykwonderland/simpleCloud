# COMP598
## Group 3:
Alice Kang 260827823

Hana Zhang 260887780

Joshua Roccamo 260669999

---

## How to Run:

To run the scripts on each server (to be set up as daemons later for RP + RM), in the home directory of the comp598-user do:
- RP: `python3 proxy.py` and `python3 job_dispatch.py`
- RM: `python3 resource_manager.py` and `python3 resource_monitor.py`
- Cloud-Client: `python3 cloud_toolset.py http://winter2023-comp598-group03-02.cs.mcgill.ca:5000 http://winter2023-comp598-group03-02.cs.mcgill.ca:7000`

Note: the job_dispatch.py file runs forever with sleeps in the middle, consistently checking for any jobs to run in the queue and any available nodes.

The monitoring dashboard needs to be run with:
- RM: `python3 cloud_dashboard.py`
It can be accessed at:
http://winter2023-comp598-group03-02.cs.mcgill.ca:80/cloudmonitor/dashboard/

---

## Servers:
- RP: winter2023-comp598-group03-01.cs.mcgill.ca
- RM: winter2023-comp598-group03-02.cs.mcgill.ca
- Cloud-Client: winter2023-comp598-group03-03.cs.mcgill.ca

---