#%% Import JupyterNotebook client
from client import JupyterNotebook

# Import libraries
import os
import uuid
import requests

# TODO check session in memory? if not -> new create or what?

class JupyterManager:
    def __init__(self, config):
        print('[__init__] Initializing Jupyter Manager')
        #  Runtime memory for linking sessions to kernel, notebook and spark session.
        print('[__init__] Setting a runtime memory for linking sessions to kernel, notebook and spark session')
        self.memory = {}
        self.cfg = config
    
    def execute_code(self, session_id, code):
        print('[__init__] Executing code on session %s'%(session_id))
        output = self.memory[session_id]['manager'].execute_code(code = code, cell_id = '', output_type = 'shell')
        return output
    
    def add_cell_and_execute(self, session_id, code, index = -1):
        print('[__init__] Adding cell and executing code on session. %s'%(session_id))
        return self.memory[session_id]['manager'].add_cell_and_execute(code = code, index = index)
    
    def add_cell(self, session_id, code, index = -1):
        print('[__init__] Adding new cell on session. %s'%(session_id))
        cell_id = self.memory[session_id]['manager'].add_cell(code = code, index = index)
        return cell_id
    
    def remove_cell(self, session_id, cell_id):
        print('[__init__] Removing cell on session. %s'%(session_id))
        self.memory[session_id]['manager'].remove_cell(cell_id)
    
    def rearrange_cells(self, session_id, cell_info):
        print('[__init__] Rearranging cells on session. %s'%(session_id))
        self.memory[session_id]['manager'].rearrange_cells(cell_info)
    
    def save_notebook(self, session_id):
        print('[__init__] Saving notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].save_notebook()

    def load_notebook(self, session_id):
        print('[__init__] Loading notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].load_notebook()

    def execute_notebook(self, session_id):
        print('[__init__] Executing notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].execute_notebook()
    
    def delete_notebook(self, session_id):
        print('[__init__] Deleting notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].delete_notebook()
    
    def clear_notebook_outputs(self, session_id):
        print('[__init__] Clearing outputs from notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].clear_notebook_outputs()
    
    def generate_python_script_from_notebook(self, session_id):
        print('[__init__] Generating python code from notebook on session. %s'%(session_id))
        self.memory[session_id]['manager'].generate_python_script_from_notebook()

    
    def delete_session(self, session_id):
        print('[__init__]  Deleting session')
        if session_id not in self.memory:
            print('[__init__] Session not found in memory')
            return False
        print('[__init__]  Closing notebook client')
        del self.memory[session_id]['manager']
        print('[__init__]  Killing kernel')
        op = self.kill_kernel(self.memory[session_id]['kernel_id'])
        if op == False:
            print('[__init__]  unable to kill kernel')
            return False
        del self.memory[session_id]
        print('[__init__]  Session deleted successfully.')
        return True

    def create_session(self, session_id, notebook_name = '', notebook_path = ''):
        print('[__init__]  Creating session')
        if notebook_name == '':
            notebook_name = str(uuid.uuid4())
        if not notebook_name.endswith('.ipynb'):
            notebook_name += '.ipynb'
        if notebook_path != '':
            notebook_path = os.path.join(self.cfg.JUPYTER_NOTEBOOK_BASE_PATH, notebook_path)
        else:
            notebook_path = self.cfg.JUPYTER_NOTEBOOK_BASE_PATH
        
        self.memory[session_id] = {}
        self.memory[session_id]['notebook_name'] = notebook_name
        self.memory[session_id]['notebook_path'] = notebook_path
        self.memory[session_id]['kernel_id'] = self.launch_kernel()
        self.memory[session_id]['kernel_file'] = os.path.join(self.cfg.KERNEL_RUNTIME_DIR, self.memory[session_id]['kernel_id'] + '.json')
        
        if self.memory[session_id]['kernel_id'] == '':
            print('[__init__]  Failed initializing kernel')
            return False
        
        print('[__init__]  Initializing Notebook')
        notebook = JupyterNotebook(notebook_name = notebook_name, notebook_path = notebook_path, kernel_info = self.cfg.KERNEL_INFO, kernel_file = self.memory[session_id]['kernel_file'])
        print('[__init__]  notebook client active')
        
        self.memory[session_id]['manager'] = notebook
        print('[__init__]  notebook client kernel ready')
        
        print('[__init__]  Connecting to kernel to spark master')
        print('[__init__]  Connecting to kernel to spark master | step 1 of 4')
        _ = notebook.execute_code(code = 'from pyspark.sql import SparkSession')
        print('[__init__]  Connecting to kernel to spark master | step 2 of 4')
        _ = notebook.execute_code(code = 'spark = SparkSession.builder.master("spark://%s:%s").getOrCreate()'%(self.cfg.SPARK_MASTER_IP, self.cfg.SPARK_MASTER_PORT))
        print('[__init__]  Connecting to kernel to spark master | step 3 of 4')
        _ = notebook.execute_code(code = 'sc = spark.SparkContext')
        print('[__init__]  Connecting to kernel to spark master | step 4 of 4')
        _ = notebook.execute_code(code = 'spark')
        
        print('[__init__]  Session created successfully.')
        return True
    
    #%% Internal functions for managing kernel
    def launch_kernel(self):
        print('[__init__]  Launching a new kernel')
        url = '%s://%s:%s/api/kernels'%(self.cfg.JUPYTER_HTTP, self.cfg.JUPYTER_IP, self.cfg.JUPYTER_PORT)
        response = requests.post(url, params = {'token': self.cfg.JUPYTER_TOKEN})
        if response.ok:
            print('[__init__]  Launch success. ID: %s'%(str(response.json()['id'])))
            return str(response.json()['id'])
        else:
            print('[__init__]  Launch failed.')
            return ""
    
    def kill_kernel(self, kernel_id):
        print('[__init__]  Killing kernel. ID: %s'%(kernel_id))
        url = '%s://%s:%s/api/kernels/%s'%(self.cfg.JUPYTER_HTTP, self.cfg.JUPYTER_IP, self.cfg.JUPYTER_PORT, kernel_id)
        response = requests.delete(url, params = {'token': self.cfg.JUPYTER_TOKEN})
        if response.ok:
            print('[__init__]  Kill success.')
            return True
        else:
            print('[__init__]  Kill failed.')
            return False
    
    def interrupt_kernel(self, kernel_id):
        print('[__init__]  Interrupting kernel. ID: %s'%(kernel_id))
        url = '%s://%s:%s/api/kernels/%s/interrupt'%(self.cfg.JUPYTER_HTTP, self.cfg.JUPYTER_IP, self.cfg.JUPYTER_PORT, kernel_id)
        response = requests.post(url, params = {'token': self.cfg.JUPYTER_TOKEN})
        if response.ok:
            print('[__init__]  Interrupt success.')
            return True
        else:
            print('[__init__]  Interrupt failed.')
            return False
    
    def restart_kernel(self, kernel_id):
        print('[__init__]  Restarting kernel. ID: %s'%(kernel_id))
        url = '%s://%s:%s/api/kernels/%s/restart'%(self.cfg.JUPYTER_HTTP, self.cfg.JUPYTER_IP, self.cfg.JUPYTER_PORT, kernel_id)
        response = requests.post(url, params = {'token': self.cfg.JUPYTER_TOKEN})
        if response.ok:
            print('[__init__]  Restart success.')
            return True
        else:
            print('[__init__]  Restart failed.')
            return False
    










