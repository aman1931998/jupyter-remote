# jupyter-spark-remote
Manage Jupyter+Spark via API

`jupyter-remote` is a ready-to-use package for Modify/Execute/Manage multiple Jupyter Notebooks programmatically and parallely, and can perform following tasks
- Connect to Jupyter Notebook and Python kernel.
- Start/Stop/Restart/Interrupt Jupyter Kernels
- Load/Save/Modify/Execute notebook (and cells of notebook) and update outputs

Jupyter Service can be integrated with Spark by connecting to Spark Master, or any other technology. `jupyter-remote` interacts Jupyter Server and supports it.

# How does it work?

`jupyter-remote` library performs three tasks collectively.
1. `KernelManager`: It makes calls to Jupyter server for Start/Stop/Restart/Interrupt kernels
2. `NotebookClient`: Replicates a Jupyter notebook. When initialized, it will create a new "notebook.ipynb" and generate a pipe to the nb, connect NB to the unique kernel. The execution of notebook elements will run on the selected kernel.
3. `JupyterManager`: Managers multiple clients. Allowing interaction with multiple python kernels.

# Connecting Jupyter NB with Spark
This step is optional and hence can be skipped if you only want to work with Jupyter.

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("spark://SPARK_MASTER_IP:SPARK_MASTER_PORT").getOrCreate()
spark
```

Once you have a client active, run above code to get a `spark` session active on the kernel.

# Usage

First, we will import libraries.

```python
from manager import JupyterManager 
import config as cfg
```

We need to set config values to connect to spark and jupyter services.

```python
cfg.JUPYTER_NOTEBOOK_BASE_PATH = os.path.join('notebook') # PATH where notebooks will be stored.
cfg.KERNEL_RUNTIME_DIR = '/home/<USER>/.local/share/jupyter/runtime/' # PATH where kernel JSON files are present on jupyter server.
# you can check the `jupyter` folder. Inside it,there will be a `runtime` folder.

cfg.SPARK_MASTER_IP = '127.0.0.1' # IP for spark master # skip if not spark
cfg.SPARK_MASTER_PORT = '7077' # Port for spark master # skip if not spark

cfg.JUPYTER_HTTP = 'http' # 'http' or 'https'
cfg.JUPYTER_IP = 'XX.XX.XXX.XX' # IP for jupyter
cfg.JUPYTER_PORT = '8888' # Port for jupyter
cfg.JUPYTER_TOKEN = '' # Token for jupyter
```

Initialize Jupyter Manager
```python
JM = JupyterManager(cfg)
```

Create a new session. When a new session is created, the provided notebook path is checked. If existing file is present, it is loaded. Else a new NB will be generated. A new python kernel is initialized and connected to it using zmq sockets. 
```python
JM.create_session(session_id = 'session1')
```

Multiple APIs have been extended for notebook cells manipulation
- add_cell(code, index = -1)
- add_cell_and_execute(code, index = -1)
- remove_cell(cell_id)
- rearrange_cells(cell_info)
- clear_notebook_outputs()
These functions can be called directly for a particular session. For eg: 
```python
JM.memory['session1'].add_cell("x = int('123')", index = -1) # appends a new cell at end.
```

Multiple APIs have been extended for notebook manipulation
- save_notebook()
- load_notebook()
- execute_notebook()
- delete_notebook()
- generate_python_script_from_notebook()

To execute any code on this kernel. We can simply call.
```python
JM.memory['session1'].execute_code("CODE", output_type = 'shell')
```
There are two possible options for output.


Delete a session. When executed, it will save the notebook, end connection to kernel, and stop the kernel itself.
```python
JM.delete_session(session_id = 'session1')
```

# Contributing
`jupyter-remote` extends packages which are part of Jupyter. With the library in initial phase, I request the fellow members of the community to take initiative with me and help improve this library. 

# Improvements

Below is the list of bugs I have identified and are WIP
1. Setup queue for each kernel to maintain order of code to be executed. If CODE1 is running on kernel and CODE2 and CODE3 are sent, they wait for kernel to be idle and then execute. Need to implement queue for correct order of execution
2. Improve NBclient handling

Below are the list of improvements to be added here
1. Enable connectivity to Spark hosted remotely via SSH.
2. use `nbformat` and `nbclient` library for handling notebook components
3. Currently, sessions are being stored on memory. Need to setup DB for it.
4. Create function to get output of a cell from ipynb file.
5. If Keyboard interrupt is sent. First kill socket connections to kernel and then kill kernel
6. Getting below error sometimes when running. Probably due to missing handling of messages.
`WARNING:traitlets:Could not destroy zmq context for <jupyter_client.blocking.client.BlockingKernelClient at object at 0x.......>`

