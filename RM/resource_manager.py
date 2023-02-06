import docker
import time

global client
global nodes
global jobs_queue

class Pod:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id
        pass
    
class Node:
    def __init__(self, name, id) -> None:
        self.name = name
        self.status = "Idle"
        self.id = id
        pass

class Job:
    def __init__(self, path, status) -> None:
        self.path = path
        self.id = id(self.path)
        self.status = status
        pass

client = docker.from_env() # TODO: need to make this work on separate VM -- add host=url

def cloud_init(client):
    try:
        network = client.networks.get('container_network')
    except docker.errors.NotFound:
        network = client.networks.create('container_network', driver='bridge')
        global default_pod
        default_pod = Pod("container_network", network.id)

    print(client.api.inspect_network (network.id))
    print('Manager waiting on containers to connect to the container_network bridge...')
    while len (network.containers) == 0:
        time.sleep (5)
        network.reload()

    container_list = []
    while 1:
        if not container_list == network.containers:
            container_list = network.containers
            for container in container_list:
                print("Container connected: \n\tName:" + container.name + "\n\tStatus: " + container.status + "\n")
                time.sleep(5)
                network.reload()

def cloud_pod_register(client, POD_NAME):
    """
    Registers a new pod with the specified name to the main resource cluster. 
    Check pod name is unique and not the current pod
    """
    print("Command unavailable due to lack of resources")

def cloud_pod_rm(POD_NAME):
    """
    Removes the specified pod. 
    Command fails if there are nodes registered to this pod or if the specified pod is the default pod.
    """
    # check if pod exists
    try:
        pod = client.networks.get(POD_NAME)
    except docker.errors.NotFound:
        print(POD_NAME + " not found")
        return
    # check if pod is the default pod
    if POD_NAME != default_pod.name:
        print(POD_NAME + " cannot be removed. It is a default pod.")
        return
    # check if there are nodes registered to the pod
    elif len(pod.containers.list()) != 0:
        print(POD_NAME + " cannot be removed. There are nodes registered to this pod.")
        return 
    # remove the pod
    else:
        pod.remove()
    return

def cloud_rm(NODE_NAME):
    """
    Removes the specified node. 
    Command fails if the name does not exist or if its status is not “Idle”
    """
    for node in client.containters.list():
        if node.name is NODE_NAME:
            if node.status is "Idle": #TODO: fix this once classes are created
                node.remove()
                return
            else:
                print(NODE_NAME + " cannot be removed. Status is not Idle.")
                return
    print(NODE_NAME + " cannot be removed. It does not exist.")