import pycurl
import sys
import os
import requests

cURL = pycurl.Curl()

def cloud_hello(url):
    cURL.setopt(cURL.URL, url)
    cURL.perform()

#------------------------TOOLSET-------------------------

def cloud_init(url):
    cURL.setopt(cURL.URL, url + '/cloud/init')
    cURL.perform()

def cloud_pod_register(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/pods/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_pod_rm(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/pods/rm/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_register(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/nodes/' + command_list[2])
        cURL.perform()
    elif len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/nodes/' + command_list[2] + '/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_rm(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/nodes/rm/' + command_list[2])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_launch(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        file_path = command_list[2]
        print(file_path)
        if (os.path.isfile(file_path)):
            files = {'files': open(file_path, 'rb')}
            ret = requests.post(url + '/cloud/jobs/launch', files=files)
            print(ret.text)
        else:
            print('Error: not a file')
    else:
        print('Error: incorrect number of arguments')

def cloud_abort(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/jobs/abort/' + command_list[2])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

#------------------------MONITORING-------------------------

def cloud_pod_ls(url):
    cURL.setopt(cURL.URL, url + '/cloudmonitor/pods/all')
    cURL.perform()

def cloud_node_ls(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/nodes/all')
        cURL.perform()
    elif len(command_list) == 4:
        #TODO: this url doesn't exist yet
        cURL.setopt(cURL.URL, url + '/cloudmonitor/nodes/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_job_ls(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/jobs/all')
        cURL.perform()
    elif len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/jobs/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments') 

def cloud_job_log(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/jobs/log/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments') 

def cloud_log_node(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/nodes/log/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments') 

#-------------------------------------------------

def main():
    rmanager_url = sys.argv[1]
    rmonitor_url = sys.argv[2]    
    while (1):
        command = input('$ ')
        #TOOLSET
        if command == 'cloud hello':
            cloud_hello(rmanager_url)
        elif command == 'cloud init':
            cloud_init(rmanager_url)
        elif command.startswith('cloud pod register'):
            cloud_pod_register(rmanager_url, command)
        elif command.startswith('cloud pod rm'):
            cloud_pod_rm(rmanager_url, command)
        elif command.startswith('cloud register'):
            cloud_register(rmanager_url, command)
        elif command.startswith('cloud rm'):
            cloud_rm(rmanager_url, command)
        elif command.startswith('cloud launch'):
            cloud_launch(rmanager_url, command)
        elif command.startswith('cloud abort'):
            cloud_abort(rmanager_url, command)
        #MONITORING
        elif command.startswith('cloud pod ls'):
            cloud_pod_ls(rmonitor_url)
        elif command.startswith('cloud node ls'):
            cloud_node_ls(rmonitor_url, command)
        elif command.startswith('cloud job ls'):
            cloud_job_ls(rmonitor_url, command)
        elif command.startswith('cloud job log'):
            cloud_job_log(rmonitor_url, command)
        elif command.startswith('cloud log node'):
            cloud_log_node(rmonitor_url, command)

if __name__ == '__main__':
    main()