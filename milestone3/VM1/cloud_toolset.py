import pycurl
import sys
import os
import requests

cURL = pycurl.Curl()

#------------------------TOOLSET-------------------------

def cloud_init(url):
    cURL.setopt(cURL.URL, url + '/cloud/init')
    cURL.perform()

def cloud_pod_register(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/pod/register/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_pod_rm(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/pod/rm/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_node_register(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/node/register/' + command_list[2] +'/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_node_rm(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/node/remove/' + command_list[2] + '/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_launch(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/pod/launch/' + command_list[2])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_resume(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/pods/resume/' + command_list[2])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_pause(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/pods/pause/' + command_list[2])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

#------------------------MONITORING-------------------------

def cloud_pod_ls(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/pods/all')
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_node_ls(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/nodes/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_log_request(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/logs')
        cURL.perform()
    else:
        print('Error: incorrect number of arguments') 

def cloud_log_pod(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloudmonitor/logs/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments') 

#------------------------ELASTICITY-------------------------

def cloud_elastic_upper(url, command):
    command_list = command.split()
    if len(command_list) == 5:
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/upper/' + command_list[3] + '/' + command_list[4])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_elastic_lower(url, command):
    command_list = command.split()
    if len(command_list) == 5:
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/lower/' + command_list[3] + '/' + command_list[4])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_elastic_enable(url, command):
    command_list = command.split()
    if len(command_list) == 6:
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/enable/' + command_list[3] + '/' + command_list[4] + '/' + command_list[5])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

def cloud_elastic_disable(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/disable/' + command_list[3])
        cURL.perform()
    else:
        print('Error: incorrect number of arguments')

#-------------------------------------------------

def main():
    rmanager_url = 'http://10.140.17.108:6002'
    rmonitor_url = 'http://10.140.17.108:6003'    
    while (1):
        command = input('$ ')
        #TOOLSET
        if command == 'cloud init':
            cloud_init(rmanager_url)
        elif command.startswith('cloud pod register'):
            cloud_pod_register(rmanager_url, command)
        elif command.startswith('cloud pod rm'):
            cloud_pod_rm(rmanager_url, command)
        elif command.startswith('cloud register'):
            cloud_node_register(rmanager_url, command)
        elif command.startswith('cloud rm'):
            cloud_node_rm(rmanager_url, command)
        elif command.startswith('cloud launch'):
            cloud_launch(rmanager_url, command)
        elif command.startswith('cloud resume'):
            cloud_resume(rmanager_url, command)
        elif command.startswith('cloud pause'):
            cloud_pause(rmanager_url, command)
        #MONITORING
        elif command.startswith('cloud pod ls'):
            cloud_pod_ls(rmonitor_url, command)
        elif command.startswith('cloud node ls'):
            cloud_node_ls(rmonitor_url, command)
        elif command.startswith('cloud log request'):
            cloud_log_request(rmonitor_url, command)
        elif command.startswith('cloud log pod'):
            cloud_log_pod(rmonitor_url, command)
        #ELASTIC
        elif command.startswith('cloud elasticity lower_threshold'):
            cloud_elastic_lower(rmanager_url, command)
        elif command.startswith('cloud elasticity upper_threshold'):
            cloud_elastic_upper(rmanager_url, command)
        elif command.startswith('cloud elasticity enable'):
            cloud_elastic_enable(rmanager_url, command)
        elif command.startswith('cloud elasticity disable'):
            cloud_elastic_disable(rmanager_url, command)

if __name__ == '__main__':
    main()
