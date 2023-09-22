# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 22:12:01 2023

@author: aman1
"""
import os
import nbformat as nf

#%% dev and poc

NOTEBOOK_ABSOLUTE_PATH = r'C:\Users\aman1\Documents\GitHub\jupyter-remote\functions\notebooks'
notebook_path = os.path.join('')
notebook_name = 'deleteme.ipynb'


# create new notebook
nb = nf.v4.new_notebook()




#%%
class NotebookClient:
    def __init__(self, notebook_path, notebook_name):
        response_json = {"status": 0, "remarks": ""}
        
        # check absolute path
        if not os.path.isdir(NOTEBOOK_ABSOLUTE_PATH):
            response_json['status'] = 1
            response_json['remarks'] = "Invalid Absolute path"
        
        # check and create notebook_path if needed
        if notebook_path != '' and not os.path.isdir(os.path.join(NOTEBOOK_ABSOLUTE_PATH, notebook_path)):
            try:
                os.makedirs(name = os.path.join(NOTEBOOK_ABSOLUTE_PATH, notebook_path), exist_ok = True)
            except:
                response_json['status'] = 1
                response_json['remarks'] = "Error creating notebook path"
        
        # setting full path
        self.full_notebook_path = os.path.join(NOTEBOOK_ABSOLUTE_PATH, notebook_path, notebook_name)
        
        # checking if nb exists
        if self._check_notebook_exists():
            self.load_notebook()
        else:
            self.save_notebook()
    
    
    
    def load_notebook(self):
        file = open(self.full_notebook_path, 'r')
        data = file.read()
        file.close()
        self.notebook = nb.v4.reads(data)
            
    
    
    
    def _check_notebook_exists(self):
        return os.path.isfile(self.full_notebook_path)





#%% testing
NOTEBOOK_ABSOLUTE_PATH = r'C:\Users\aman1\Documents\GitHub\jupyter-remote\functions\notebooks'
notebook_path = os.path.join('')
notebook_name = 'deleteme.ipynb'



# create nb client for a notebook of a session
nc = NotebookClient(notebook_path = notebook_path, notebook_name = notebook_name)

