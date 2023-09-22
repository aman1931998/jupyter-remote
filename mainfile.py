




'''import os
import requests

from manager import JupyterManager
import config as cfg

#%% setting config data
cfg.JUPYTER_NOTEBOOK_BASE_PATH = os.path.join('notebook') # PATH where notebooks will be stored
cfg.KERNEL_RUNTIME_DIR = '/home/aman/.local/share/jupyter/runtime/' # PATH where kernel JSON files are present on jupyter server

cfg.SPARK_MASTER_IP = '127.0.0.1' # IP for spark master
cfg.SPARK_MASTER_PORT = '7077' # Port for spark master

cfg.JUPYTER_HTTP = 'http' # 'http' or 'https'
cfg.JUPYTER_IP = '192.168.36.130' # IP for jupyter
cfg.JUPYTER_PORT = '8888' # Port for jupyter
cfg.JUPYTER_TOKEN = 'fe9f20ed5ddfd61e392f3a2fd862d2a5b7168e854ecc96c2' # Token for jupyter



# Initialize manager
JM = JupyterManager(cfg)

# Create a new session (containing kernel, notebook and sockets)
JM.create_session(session_id = 'session1')

'''