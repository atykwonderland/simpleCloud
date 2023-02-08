import pycurl
import sys
import os
import requests

cURL = pycurl.Curl()

def cloud_hello(url):
    cURL.setopt(cURL.URL, url)
    cURL.perform()

#------------------------ALICE-------------------------

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
        ret = requests.delete(url + '/cloud/pods/' + command_list[3])
        print(ret.text)
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
        ret = requests.delete(url + '/cloud/nodes/' + command_list[2])
        print(ret.text)
    else:
        print('Error: incorrect number of arguments')

#------------------------HANA-------------------------

def cloud_launch(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        file_path = command[2]
        if (os.path.isfile(file_path)):
            file = {'files': open(file_path, 'rb')}
            ret = requests.post(url + '/cloud/jobs/launch', file = file)
            print(ret.text)
        else:
            print('Error: not a file')
    else:
        print('Error: incorrect number of arguments')
        
def cloub_abort(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        ret = request.delete(url + '/cloud/jobs/abort/' + command_list[2])
        print(ret.text)
    else:
        print('Error: incorrect number of arguments')

#-------------------------------------------------

#TODO: anything with pass needs a new method to replace it below
def main():
    rm_url = sys.argv[1]
    while (1):
        command = input('$ ')
        if command == 'cloud hello':
            cloud_hello(rm_url)
        elif command == 'cloud init':
            cloud_init(rm_url)
        elif command.startswith('cloud pod register'):
            cloud_pod_register(rm_url, command)
        elif command.startswith('cloud pod rm'):
            cloud_pod_rm(rm_url, command)
        elif command.startswith('cloud reigster'):
            cloud_register(rm_url, command)
        elif command.startswith('cloud rm'):
            cloud_rm(rm_url, command)
        elif command.startswith('cloud launch'):
            cloud_launch(rm_url, command)
        elif command.startswith('cloud abort'):
            pass

if __name__ == '__main__':
    main()
