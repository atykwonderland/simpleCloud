# COMP598
Group 3

Servers:
- RP: winter2023-comp598-group03-01.cs.mcgill.ca
- RM: winter2023-comp598-group03-02.cs.mcgill.ca
- Cloud: winter2023-comp598-group03-03.cs.mcgill.ca

Supported Commands:
| command            | input              | description                                                                                                                                                                                                                                                                      |
|--------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| cloud init         |                    | Initializes the main resource cluster. <br>All cloud services are setup.                                                                                                                                                                                                         |
| cloud pod register | POD_NAME           | This command is currently unsupported <br>we are only considering a single resource pod                                                                                                                                                                                          |
| cloud pod rm       | POD_NAME           | Removes the specified pod. <br>The command fails if there are nodes registered to this pod <br>or if the specified pod is the default pod.                                                                                                                                       |
| cloud register     | NODE_NAME [POD_ID] | Creates a new node and registers it to the specified pod ID. <br>If no pod ID was specified, the newly created node is registered to the default pod. <br>The command fails if the pod ID does not exist.                                                                        |
| cloud rm           | NODE_NAME          | Removes the specified node. <br>The command fails if the namedoes not exist or if its status is not IDLE.                                                                                                                                                                        |
| cloud launch       | PATH_TO_JOB        | Launches a specified job. <br>The job here may be a simple shell script that continuously prints out some text <br>to stdout and then waits for a few seconds.                                                                                                                   |
| cloud abort        | JOB_ID             | Aborts the specified job. <br>The command fails if the job does not exist or if it has completed. <br>If the job is registered, it is removed from the waiting queue in the manager. <br>If the job is running, it is assigned to abort and the corresponding node becomes IDLE. |

To run the scripts on each server (to be set up as daemons later for RP + RM):
RP: python3 proxy.py
RM: python3 resource_manager.py
Cloud-Client: python3 cloud_toolset.py http://winter2023-comp598-group03-03.cs.mcgill.ca:5000

for resource monitor testing, CURL each endpoint (check tutorial for how to)