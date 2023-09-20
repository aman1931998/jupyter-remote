# import libraries
import re
import os
import json
import queue
import random
from jupyter_client.consoleapp import JupyterConsoleApp

# from logger import logger

class JupyterNotebook:
    def __init__(self, notebook_name, notebook_path, kernel_info, kernel_file):
        '''
        Initializes the Jupyter Notebook client.

        Parameters
        ----------
        notebook_name : str
            Name of the notebook
        notebook_path : str
            Full path of the notebook
        kernel_info : dict
            Kernel information
        kernel_file : str
            Full path of kernel-[a-z0-9]*.json

        Returns
        -------
        None.

        '''
        if not notebook_name.endswith('.ipynb'):
            notebook_name += '.ipynb'
        print('[__init__] Initializing Session: Session Name: %s'%(notebook_name))
        print('[__init__] Setting attributes.')
        print('[__init__] Initializing Session: Session Name: %s'%(notebook_name))
        self.notebook_name, self.notebook_path, self.kernel_info, self.kernel_file, self.cell_info = notebook_name, notebook_path, kernel_info, kernel_file, []
        print('[__init__] notebook_name: %s'%(self.notebook_name))
        print('[__init__] notebook_path: %s'%(self.notebook_path))
        print('[__init__] kernel_file: %s'%(self.kernel_file))
        self.d = {'nbformat': 4, 
                  'nbformat_minor': 5, 
                  'cells': [], 
                  'metadata': {
                      'kernelspec':self.kernel_info['metadata.kernelspec']
                      }
                }
        
        print('[__init__] Creating folder path if needed')
        os.makedirs(self.notebook_path, exist_ok = True)

        print('[__init__] Checking if notebook exists or not')
        self.client, self.kernel, self.execution_status = None, None, None
        self.connect_to_kernel()
        print('[__init__] Connection established.')

        # TESTING
        # self.outputs = []
        # config
        self.kernel_status_check_timeout = 0.1
    
    #%% kernel and execution
    def connect_to_kernel(self):
        '''
        Connect to Jupyter Kernel

        Returns
        -------
        None.

        '''
        print('[connect_to_kernel] Setting connection details')
        self.client = JupyterConsoleApp(sconnection_file = self.kernel_file)

        self.client.existing = self.kernel_file[self.kernel_file.rindex('/') + 1:]
        self.client.runtime_dir = self.kernel_file[:self.kernel_file.rindex('/')]

        print('[connect_to_kernel] Initializing kernel_client')
        self.client.initialize()

        print('[connect_to_kernel] Getting kernel')
        self.kernel = self.client.blocking_client()
        self.execution_status = 'idle'
    
    def execute_code(self, code = '', cell_id = '', output_type = 'shell'):
        '''
        Executes code provided. If cell_id is provided, means some cell has to be executed, hence notebook output is also updated.

        Parameters
        ----------
        code : str, optional
            Code. The default is ''.
        cell_id : str, optional
            cell_id. The default is ''.
        output_type : str, optional
            "shell" or "cell". The default is 'shell'.

        Returns
        -------
        dict
            Output based on output_type - shell output or cell output

        '''
        print('[execute_code] running _execute_code()')
        output = self._execute_code(code = code, cell_id = cell_id)
        execution_count = output['execution_count']
        if cell_id != '':
            print('[execute_code] msg_id = %s'%(cell_id))
            print('[execute_code] Parsing output for both service and notebook')
            output = self.parse_output(output['stdout'], output_type = 'both')
            print('[execute_code] updating notebook\'s cell output')
            self._update_cell_output(cell_id, output['cell'], execution_count)
            self.save_notebook()
            return output[output_type]
        else:
            print('[execute_code] parsingoutput for service')
            op = self.parse_output(output['stdout'], output_type = output_type)
            return op
    
    def add_cell_and_execute(self, code, index = -1):
        '''
        Adds a new cell to the notebook and execute the cell.

        Parameters
        ----------
        code : str
            Code input
        index : int, optional
            index at which cell should be added. The default is -1.

        Returns
        -------
        dict
            Consisting of output and cell_id.

        '''
        print('[add_cell_and_execute] Creating new cell, adding code and execute')
        cell_id = self.add_cell(code = code, index = index)
        output = self._execute_code(code = code, cell_id = '')
        parsed_output = self.parsed_output(output['stdout'], output_type = 'both')
        self._update_cell_output(cell_id = cell_id, output = parsed_output['cell'], execution_count = output['execution_count'])
        self.save_notebook()
        return {"output": parsed_output['shell'], 'cell_id': cell_id}
    
    #%% cell manipulation
    def add_cell(self, code, index = -1): # front
        print('[add_cell] Adding a new cell')
        cell = {'id': self.generate_cell_id(8), 
                'cell_type': 'code', 'metadata': {}, 
                'source': code, 'outputs': [], 
                'execution_count': None}
        if index == -1:
            self.d['cells'].append(cell)
            self.cell_info.append(cell['id'])
        else:
            self.d['cells'].insert(index, cell)
            self.cell_info.insert(index, cell['id'])
        self.save_notebook()
        return cell['id']
        
    def remove_cell(self, cell_id): # front
        print('[remove_cell] Remove cell ID: %s'%(cell_id))
        index = self.cell_info.index(cell_id)
        del self.cell_info[index], self.d['cells'][index]
        self.save_notebook()
    
    def rearrange_cells(self, cell_info):
        print('[rearrange_cells] Checking if input is correct.')
        assert set(cell_info) == set(self.cell_info)
        print('[rearrange_cells] Rearranging cells.')
        self.d['cells'] = [self.d['cells'][self.cell_info.index(i)] for i in cell_info]
        self.cell_info = cell_info
        self.save_notebook()
    
    def _update_cell_output(self, cell_id, output, execution_count):
        self.d['cells'][self.cell_info.index(cell_id)]['outputs'] = output
        self.d['cells'][self.cell_info.index(cell_id)]['execution_count'] = execution_count
    
    
    #%% notebook manipulation
    # ek function bana do for creating local and remote pipe to notebook.ipynb file. and call that pipe function to each nb manipulation functions
    def save_notebook(self):
        try:
            print('[save_notebook] Saving Notebook.')
            f = open(os.path.join(self.notebook_path, self.notebook_name), 'w')
            json.dump(self.d, f)
            f.close()
            return True
        except BaseException as e:
            print('[save_notebook] Saving Notebook: Failure: %s'%(str(e)))
            return False
    
    def load_notebook(self):
        try:
            print('[load_notebook] Checking if input is correct.')
            f = open(os.path.join(self.notebook_path, self.notebook_name), 'r')
            json_data = f.read()
            self.d = json.loads(json_data)
            f.close()
            print('[load_notebook] Attaching latest kernel metadata to the notebook.')
            self.d['metadata'] = {"kernelspec": self.kernel_info['metadata.kernelspec'], 'language_info': {'name': 'python', 'codemirror_mode': {'name': 'ipython', 'version': 3}, 'file_extension': '.py', 'mimetype': 'text/x-python', 'pygments_lexer': 'ipython3', 'nbconvert_exporter': 'python', 'version': self.kernel_info['metadata.language_info.version']}}
            self.cell_info = [i['id'] for i in self.d['cells']]
            print('[load_notebook] Notebook successfully loaded.')
            return True
        except BaseException as e:
            print('[load_notebook] Saving Notebook: Failure: %s'%(str(e)))
            return False
    
    def execute_notebook(self): # add check for failure. # Halt the notebook
        result = {"status": 0, 'cell_id': None}
    
        print('[execute_notebook] Executing complete notebook')
        for cell_id in self.cell_info:
            print('[execute_notebook] Executing cell: %s'%(cell_id))
            output = self._execute_code(code = '', cell_id = cell_id)
            parsed_output = self.parse_output(output['stdout'], output_type = 'both')
            self._update_cell_output(cell_id = cell_id, output = parsed_output['cell'], execution_count = output['execution_count'])
            for i in output['cell']:
                if i['output_type'] == 'error':
                    print('[execute_notebook] Traceback at cell: %s'%(cell_id))
                    result['status'] = 1
                    result['cell_id'] = cell_id
                    break
            self.save_notebook()
        print('[execute_notebook] notebook execution completed' + ("" if result['status'] == 0 else " but errors have occured."))
        return result
    
    def delete_notebook(self):
        try:
            print('[delete_notebook] Deleting notebook: %s'%(self.notebook_path))
            os.remove(self.notebook_path)
            return True
        except:
            print('[delete_notebook] Failed deleting notebook: %s'%(self.notebook_path))
            return False
    
    def clear_notebook_outputs(self):
        print('[delete_notebook] Clearing all outputs')
        for i in self.d['cells']:
            i['outputs'] = []
        self.save_notebook()
    
    def generate_python_script_from_notebook(self):
        code = ""
        for i in self.d['cells']:
            temp = ""
            if type(i['source']) == list:
                temp += "\n".join(i['source'])
            else:
                temp += i['source']
            code += temp
        return code
    
    def generate_cell_id(self, n = 8):
        s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        id_ = ""
        for i in range(n):
            id_ += random.choice(s)
        return id_

    #%% output parsers
    def parse_error(self, error_content, output_type = 'cell'): # need to prettify this functionf for shell
        # input
        parsed_error = None
        if output_type == 'cell':
            error_content['output_type'] = 'error'
            parsed_error = error_content
        else: # output_type = 'shell':
            parsed_error = error_content
        return parsed_error
    
    def parse_output(self, data, output_type = 'cell'): # ['shell', 'cell', 'both']
        output_cell = []
        output_shell = {'stream': '', 
                        'display_data': [], 
                        'execute_result': [], 
                        'error': []}
        if output_type in ['cell', 'both']:
            for info in data: # info = data[0]
                if info['type'] == 'stream': 
                    text = info['output']['text']
                    flag = text.endswith('\n')
                    text = text.split('\n')
                    if len(text) > 0 and type(text[-1]) == str and flag: 
                        text[-1] += '\n'
                    output_cell.append({'output_type': 'stream', 
                                        'name': info['output']['name'], 
                                        'text': text})
                elif info['type'] == 'display_data': 
                    output_cell.append({'output_type': 'display_data', 
                                        'data': info['output']['data'], 
                                        'metadata': info['output']['metadata']})
                elif info['type'] == 'execute_result': 
                    output_cell.append({'output_type': 'execute_result', 
                                        'data': info['output']['data'], 
                                        'metadata': info['output']['metadata'], 
                                        'execution_count': info['output']['execution_count']})
                else: # info['type'] == 'error': 
                    info['output']['output_type'] = 'error'
                    output_cell.append(self.parse_error(info['output'], output_type = output_type))
        if output_type in ['shell', 'both']:
            for info in data: # info = data[0]
                if info['type'] == 'stream':
                    output_shell['stream'] += info['output']['text']
                elif info['type'] == 'display_data':
                    output_shell['display_data'].append(info['output'])
                elif info['type'] == 'execute_result':
                    if 'execution_count' in info['output']:
                        del info['output']['execution_count']
                    output_shell['execute_result'].append(info['output'])
                else: # info['type'] == 'error':
                    output_shell['error'].append(self.parse_error(info['output'], output_type = output_type))
            # output_shell = json_dumps(output_shell)
        if output_type == 'both':
            return {'cell': output_cell, 'shell': output_shell}
        elif output_type == 'cell':
            return output_cell
        else: # output_type == 'shell':
            return output_shell
    
    # internal function for code execution
    def _execute_code(self, code = '', cell_id = ''):
        '''
        

        Parameters
        ----------
        code : str, optional
            code to execute. The default is ''.
        cell_id : str, optional
            DESCRIPTION. The default is ''.

        Returns
        -------
        dict
            Output dictionary with following keys: ['status', 'remarks', 'code', 'stdout', 'stderr', 'shell_output', 'log', 'msg_id', 'execution_start_time', 'execution_end_time', 'execution_count']
        '''
        
        if bool(code) == False and bool(cell_id) == False:
            return {'status': 1, 'remarks': 'invalid inputs to execute_code'}
        
        if cell_id != "": # TODO create a function to get the code from cell_id
            if not self._check_cell_id(cell_id):
                return {'status': 1, 'remarks': 'cell_id %s not found'%(cell_id)}
            code = self.d['cells'][self.cell_info.index(cell_id)['source']]
        
        if type(code) == list:
            code = "\n".join(code)
        print('[_execute_code] Code: %s'%(code))
        
        output = {'status': 0, 'remarks': '', 'code': code, 
                  'stdout': [], 'stderr': [], 'shell_output': [], 
                  'log': [], 'msg_id': None, 
                  'execution_start_time': None, 'execution_end_time': None, 'execution_count': None}
        
        error_flag = False
        print('[_execute_code] Executing code')
        try:
            msg_id = self.kernel.execute(code)
            print('[_execute_code] Code Submitted: Msg ID: %s'%(msg_id))
            output['msg_id'] = msg_id
        except BaseException as e:
            error_flag = True
            output['status'] = 1 # failure in execution
            output['stderr'].append(str(e))
            print('[_execute_code] Error during code request: %s'%(str(e)))
        
        if not error_flag:
            print('[_execute_code] Outputs....')
            flag = True
            print('[_execute_code] Getting iopub messages')
            while flag:
                try:
                    op = self.kernel.get_iopub_msg(timeout = self.kernel_status_check_timeout)
                    print(op)
                    print('[_execute_code] iopub message received')
                    output['log'].append(op)
                    
                    if op['msg_type'] in ['stream', 'display_data', 'execute_result', 'error']:
                        print('[_execute_code] [iopub] msg_type = %s'%(op['msg_type']))
                        print(output)
                        output['stdout'].append({'type': op['msg_type'], 'output': op['content']})
                    
                    elif op['msg_type'] == 'status':
                        print('[_execute_code] [iopub] msg_type = status')
                        
                        if op['content']['execution_state'] == 'busy':
                            print('[_execute_code] [iopub] execution_state = busy')
                            self.execution_status = 'busy'
                            output['execution_start_time'] = op['header']['date']
                            continue
                        
                        elif op['content']['execution_state'] == 'idle':
                            print('[_execute_code] [iopub] execution_state = idle')
                            self.execution_status = 'idle'
                            output['execution_end_time'] = op['header']['date']
                            flag = False
                        
                        elif op['content']['execution_state'] == 'starting':
                            print('[_execute_code] [iopub] execution_state = idle')
                            self.execution_status = 'idle'
                            output['execution_end_time'] = op['header']['date']
                        
                        else:
                            print('[_execute_code] [iopub] execution_status = ELSE')
                            print(op)
                    
                    elif op['msg_type'] == 'execute_input':
                        print('[_execute_code] [iopub] msg_type = execute_input')
                        output['execution_count'] = op['content']['execution_count']
                    
                    else:
                        print('[_execute_code] [iopub] msg_tye = ELSE')
                        print(op)
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    break
                except BaseException as e:
                    print('[_execute_code] ERROR in interface.' + str(e))
            print('[_execute_code] Getting shell messages')
            while True:
                try:
                    output['shell_output'].append(self.kernel.get_shell_msg(timeout = self.kernel_status_check_timeout))
                    print('[_execute_code] shell message received')
                except queue.Empty:
                    break
        print('[_execute_code] Code execution completed')
        return output
    
    def _check_cell_id(self, cell_id):
        return cell_id in self.cell_info
    
    def get_cell_output(self, cell_id):
        pass # TODO


































