import docker
import time
client = docker.from_env()

try:
    network = client.networks.get('container_network')
except docker.errors.NotFound:
    network = client.networks.create('container_network', driver='bridge')

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
            print("Container connected: \n\tName: + container.name + "\n\tStatus: " + container.status + "\n")
            time.sleep(5)
            network.reload()