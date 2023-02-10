import docker

client = docker.from_env()
[img, logs] = client.images.build(path='/home/comp598-user/monitoring_html', rm=True, dockerfile='/home/comp598-user/monitoring_html/Dockerfile')

for l in logs:
    print(l)

container = client.containers.run(img, detach=True, ports={'80/tcp':'80'})