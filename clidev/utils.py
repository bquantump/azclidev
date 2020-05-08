import clidev as cli
import os
import subprocess


def validate_env():
    if not os.environ.get(cli.VIRTUAL_ENV):
        raise RuntimeError("You are not running inside a virtual enviromet")
    if not os.environ.get(cli.AZ_CONFIG_DIR):
        raise RuntimeError(
            "AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    if not os.path.exists(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config")):
        raise RuntimeError(
            "The Azure config file does not exist. please rerun setup")


def edit_activate(azure_config_path, dot_azure_config):
    if cli.IS_WINDOWS:
        ps1_edit(azure_config_path, dot_azure_config)
        bat_edit(azure_config_path, dot_azure_config)
    else:
        unix_edit(azure_config_path, dot_azure_config)


def unix_edit(azure_config_path, dot_azure_config):
    activate_path = os.path.join(azure_config_path, cli.UN_BIN,
                                 cli.UN_ACTIVATE)
    content = open(activate_path, "r").readlines()

    # check if already ran setup before
    if cli.AZ_CONFIG_DIR not in content[0]:
        content = [cli.AZ_CONFIG_DIR + '=' + dot_azure_config + '\n',
                   cli.UN_EXPORT + ' ' + cli.AZ_CONFIG_DIR + '\n'] + content
        with open(activate_path, "w") as file:
            file.writelines(content)


def bat_edit(azure_config_path, dot_azure_config):
    activate_path = os.path.join(azure_config_path, cli.SCRIPTS,
                                 cli.BAT_ACTIVATE)
    content = open(activate_path, "r").readlines()
    if cli.AZ_CONFIG_DIR not in content[1]:
        content = content[0:1] + ['set ' + cli.AZ_CONFIG_DIR +
                                  '=' + dot_azure_config + '\n'] + content[1::]
        with open(activate_path, "w") as file:
            file.writelines(content)


def ps1_edit(azure_config_path, dot_azure_config):
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
    with open(activate_path, "w") as file:
        file.write(content)


def install_cli(cli_path, venv_path):
    venv_path = os.environ[cli.VIRTUAL_ENV] = venv_path
    src_path = os.path.join(cli_path, 'src')
    activate_path = os.path.join(venv_path, 'Scripts', 'activate') if cli.IS_WINDOWS else '.\ ' + os.path.join(
        venv_path, cli.UN_BIN, cli.UN_ACTIVATE)
    delimiter = ' && ' if cli.IS_WINDOWS else '; '
    executable = None if cli.IS_WINDOWS else cli.BASH_EXE
    print("\nactivate path is " + str(activate_path))
    subprocess.call(activate_path + delimiter +
                    'pip install azure-common', shell=True, executable=None)
    subprocess.call(activate_path + delimiter + cli.PIP_E_CMD +
                    os.path.join(src_path, 'azure-cli-nspkg'), shell=True, executable=executable)
    subprocess.call(activate_path + delimiter + cli.PIP_E_CMD +
                    os.path.join(src_path, 'azure-cli-telemetry'), shell=True, executable=executable)
    subprocess.call(activate_path + delimiter + cli.PIP_E_CMD +
                    os.path.join(src_path, 'azure-cli-core'), shell=True, executable=executable)
    subprocess.call(activate_path + delimiter + cli.PIP_E_CMD +
                    os.path.join(src_path, 'azure-cli'), shell=True, executable=executable)
    subprocess.call(activate_path + delimiter + cli.PIP_E_CMD +
                    os.path.join(src_path, 'azure-cli-testsdk'), shell=True, executable=executable)
