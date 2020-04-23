import clidev as cli
import os

def validateConfig(content):
    indexOfExtensions = content.index("[extension]")
    if (indexOfExtensions < 0 or len(content) <= indexOfExtensions + 2 or 
        content[indexOfExtensions + 1] != cli.AZ_DEV_SRC or
        content[indexOfExtensions + 2] != '='):
        raise RuntimeError("the extensions dir is not setup correctly. Please rerun setup")
    if not os.path.isdir(content[indexOfExtensions + 3]):
        raise RuntimeError("the path to the cli extensions does not exist"
                        " try running setup again with a valid extensions dir")
    return content[indexOfExtensions + 3]

def validateEnv():
    if not os.environ.get(cli.VIRTUAL_ENV):
        raise RuntimeError("You are not running inside a virtual enviromet")
    if not os.environ.get(cli.AZ_CONFIG_DIR):
        raise RuntimeError(
            "AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    if not os.path.exists(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config")):
        raise RuntimeError(
            "The Azure config file does not exist. please rerun setup")
        
# @TODO set AZURE_CLI_DIR if exist and AZURE_REST_SPEC_DIR if exist    
def setConfig():
    with open(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config"), "r") as file:
        content = file.read()
        content = content.split()
        os.environ["AZURE_EXTENSION_DIR"] = validateConfig(content)