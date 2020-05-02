import sys

CONFIG_NAME = 'config'
ACTIVATE_PS = 'Activate.ps1'
PS1_VENV_SET = '$env:VIRTUAL_ENV'
SCRIPTS = 'Scripts'
VIRTUAL_ENV = 'VIRTUAL_ENV'
VENV_CMD = 'python -m venv --system-site-packages '
AZ_CONFIG_DIR = 'AZURE_CONFIG_DIR'
AZ_DEV_SRC = 'dev_sources'
AZ_CLOUD = {'name': 'AzureCloud'}
CLOUD_SECTION = 'cloud'
EXT_SECTION = 'extension'
CLI_SECTION = 'clipath'
REST_SPEC_SECTION = 'restspec'
EVN_AZ_CONFIG = '$env:AZURE_CONFIG_DIR'
AZEX_PREFIX = 'azext_'
INSTALL_EXT_CMD = 'pip install -e .'
PIP_E_CMD = 'pip install -e '
IS_WINDOWS = sys.platform.lower() in ['windows', 'win32']