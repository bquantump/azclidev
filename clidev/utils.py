import clidev as cli
import os
import subprocess

def validateEnv():
    if not os.environ.get(cli.VIRTUAL_ENV):
        raise RuntimeError("You are not running inside a virtual enviromet")
    if not os.environ.get(cli.AZ_CONFIG_DIR):
        raise RuntimeError(
            "AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    if not os.path.exists(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config")):
        raise RuntimeError(
            "The Azure config file does not exist. please rerun setup")

def edit_activate(azure_config_path, dot_azure_config):
    ## windows only for now, will check linux later
    activate_path = os.path.join(azure_config_path, cli.SCRIPTS,
                                 cli.ACTIVATE_PS)
    content = open(activate_path, "r").read()
    idx = content.find(cli.PS1_VENV_SET)
    if idx < 0:
        raise RuntimeError("hmm, it looks like " + cli.ACTIVATE_PS + " does"
                           " not set the virutal enviroment variable VIRTUAL_ENV")
    if content.find(cli.EVN_AZ_CONFIG) < 0:
        content = content[:idx] + cli.EVN_AZ_CONFIG + " = " + \
            "\"" + dot_azure_config + "\"; " + \
            content[idx:]
    file = open(activate_path, 'w')
    file.write(content)
    file.close()
        
def install_cli(cli_path, venv_path):
    venv_path = os.environ[cli.VIRTUAL_ENV] = venv_path
    src_path = os.path.join(cli_path, 'src')
    site_pkgs = os.path.join(venv_path, 'Lib', 'site-packages')
    activate_path = os.path.join(venv_path, 'Scripts', 'activate')
    subprocess.call(activate_path + ' && ' + 'pip install azure-common', shell=True)
    subprocess.call(activate_path + ' && ' + cli.PIP_E_CMD + os.path.join(src_path, 'azure-cli-nspkg'), shell=True)
    subprocess.call(activate_path + ' && ' + cli.PIP_E_CMD + os.path.join(src_path, 'azure-cli-telemetry'), shell=True)
    subprocess.call(activate_path + ' && ' + cli.PIP_E_CMD + os.path.join(src_path, 'azure-cli-core'), shell=True)
    subprocess.call(activate_path + ' && ' + cli.PIP_E_CMD + os.path.join(src_path, 'azure-cli'), shell=True)
    subprocess.call(activate_path + ' && ' + cli.PIP_E_CMD + os.path.join(src_path, 'azure-cli-testsdk'), shell=True)