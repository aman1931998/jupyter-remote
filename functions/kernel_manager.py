#%% Import Libraries
import os
import requests
import json

#from .. import message_formats as mf

class KernelManager:
    def __init__(self, cfg):
        self.JUPYTER_HTTP = cfg.HTTP
        self.JUPYTER_IP = cfg.IP
        self.JUPYTER_PORT = cfg.PORT
        self.JUPYTER_TOKEN = cfg.TOKEN

        self.JUPYTER_URL = "%s://%s:%s"%(self.JUPYTER_HTTP, self.JUPYTER_IP, self.JUPYTER_PORT)
    
    def launch_kernel(self):
        print('[KernelManager][launch_kernel]Launching kernel')
        url = '%s/api/kernels'%(self.JUPYTER_URL)
        response = requests.post(url, params = {
            'token': self.JUPYTER_TOKEN
        })
        if response.ok:
            print('[KernelManager][launch_kernel]Launch success. ID: %s'%(str(response.json()['id'])))
            return str(response.json()['id'])
        else:
            print('[KernelManager][launch_kernel]Launch failed.')
            return ""
    
    def kill_kernel(self, kernel_id):
        '''0 -> kill success | 1 -> kill failed | -1 -> kernel not found'''
        print('[KernelManager][kill_kernel]Killing kernel. ID: %s'%(kernel_id))
        url = '%s/api/kernels/%s'%(self.JUPYTER_URL, kernel_id)
        response = requests.delete(url, params = {
            'token': self.JUPYTER_TOKEN
        })
        if response.ok:
            print('[KernelManager][kill_kernel]Kernel killed successfully. ID: %s'%(kernel_id))
            return 0
        elif response.status_code == 404:
            print('[KernelManager][kill_kernel]Kernel not found. ID: %s'%(kernel_id))
            return -1
        else:
            print('[KernelManager][kill_kernel]Kill failed. Reason: %s'%(response.json()['message']))
            return 1
    
    def interrupt_kernel(self, kernel_id):
        '''0 -> interrupt success | 1 -> interrupt failed | -1 -> kernel not found'''
        print('[KernelManager][interrupt_kernel]Interrupting kernel. ID: %s'%(kernel_id))
        url = '%s/api/kernels/%s/interrupt'%(self.JUPYTER_URL, kernel_id)
        response = requests.post(url, params = {
            'token': self.JUPYTER_TOKEN
        })
        if response.ok:
            print('[KernelManager][interrupt_kernel]Kernel interrupted successfully. ID: %s'%(kernel_id))
            return 0
        elif response.status_code == 404:
            print('[KernelManager][interrupt_kernel]Kernel not found. ID: %s'%(kernel_id))
            return -1
        else:
            print('[KernelManager][interrupt_kernel]Interrupt failed. Reason: %s'%(response.json()['message']))
            return 1
    
    def restart_kernel(self, kernel_id):
        '''0 -> restart success | 1 -> restart failed | -1 -> kernel not found'''
        print('[KernelManager][restart_kernel]Restarting kernel. ID: %s'%(kernel_id))
        url = '%s/api/kernels/%s/restart'%(self.JUPYTER_URL, kernel_id)
        response = requests.post(url, params = {
            'token': self.JUPYTER_TOKEN
        })
        if response.ok:
            print('[KernelManager][restart_kernel]Kernel restarted successfully. ID: %s'%(kernel_id))
            return 0
        elif response.status_code == 404:
            print('[KernelManager][restart_kernel]Kernel not found. ID: %s'%(kernel_id))
            return -1
        else:
            print('[KernelManager][restart_kernel]Restart failed. Reason: %s'%(response.json()['message']))
            return 1









#%% TESTING
token = 'ff772516a08c2a77ecf7c651a33244bacaaf30d81fbeaf97'
ip = '192.168.36.130'
port = '8888'
http = 'http'
