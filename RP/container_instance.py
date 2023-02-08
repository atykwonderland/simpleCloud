import docker

client = docker.from_env()

container = client.containers.run(image = "bfirsh/reticulate-splines", detach=True, network="container_network")