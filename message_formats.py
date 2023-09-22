
#%% Jupyter Server configuration
class JupyterConfig:
    def __init__(self, jupyter_http = '', jupyter_ip = '', jupyter_port = '', jupyter_token = ''):
        self.HTTP = jupyter_http
        self.IP = jupyter_ip
        self.PORT = jupyter_port
        self.TOKEN = jupyter_token
