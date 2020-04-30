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
        
def install_cli(cli_path, venv_path):
    venv_path = os.environ[cli.VIRTUAL_ENV] = venv_path
    src_path = os.path.join(cli_path, 'src')
    site_pkgs = os.path.join(venv_path, 'Lib', 'site-packages')
    activate_path = os.path.join(venv_path, 'Scripts', 'activate')
    subprocess.call(activate_path + ' && ' + 'pip install azure-common', shell=True)
    subprocess.call(activate_path + ' && ' + 'pip install -e ' + os.path.join(src_path, 'azure-cli-nspkg'), shell=True)
    subprocess.call(activate_path + ' && ' + 'pip install -e ' + os.path.join(src_path, 'azure-cli-telemetry'), shell=True)
    subprocess.call(activate_path + ' && ' + 'pip install -e ' + os.path.join(src_path, 'azure-cli-core'), shell=True)
    subprocess.call(activate_path + ' && ' + 'pip install -e ' + os.path.join(src_path, 'azure-cli'), shell=True)
    subprocess.call(activate_path + ' && ' + 'pip install -e ' + os.path.join(src_path, 'azure-cli-testsdk'), shell=True)