import os
import sys
import subprocess
import constants
from shutil import copyfile

if __name__ == "__main__":
    # this will parse command line arguments to trigger the correct funtions to be called
    # For example, if setup -r path is passed in, the setupConfig(path)
    pass

def setupConfig(pathToCliExtensionRepo):
    # this will setup up the CLI extension that that az will use the cli
    # extenison in the current virual enviroment
    # It should: 
    # validate virtual env exist
    # copy over .azure/config if it exist in user global .azure dir
    # make .azure/config if it does not exist
    # customize the .ps1 and .bat activation scripts to setup
    # the needed env vars
    
    # first cut, need to check if dirs already exist and files already
    # exist. Parse those files to see if things are already setup etc
    if not os.environ.get('VIRTUAL_ENV'):
        raise RuntimeError("you are not running inside a virtual enviromet or VIRTUAL_ENV is not set")
    path = os.path.join(os.environ.get('VIRTUAL_ENV'), '.azure')
    os.mkdir(path)
    if os.path.isfile(os.path.expanduser(os.path.join('~', '.azure')) + 
                      constants.CONFIG_NAME):
        copyfile(os.path.expanduser(os.path.join('~', '.azure')) + 
                 constants.CONFIG_NAME, path)
    content = open(path + constants.CONFIG_NAME, "r+").readline()
    file = open(path + constants.CONFIG_NAME, "w")
    if constants.EXTENSION_TAG not in content:
        content += [constants.CONFIG_NAME, "dev_sources = " + pathToCliExtensionRepo + "\n"]
        file.writelines(content)
    else:
        content[content.index(constants.CONFIG_NAME) + 1] = "dev_sources = " + pathToCliExtensionRepo + "\n"
        file.writelines(content)
    file.close()
    
            
            
    
    # write set env var in env activation scripts, .ps1
    

def setupTestEnv():
    # this will setup pytest for CLI extension to run 
    # in a clean enviroment. It will allow the user to customize
    # pytest commands or use a default set of pytest commands
    # it will also clean up the test enviroment unless the user specifies 
    # otherwise
    
    
    if not os.environ.get("AZURE_CONFIG_DIR"):
        raise RuntimeError("AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    with open(os.environ["AZURE_CONFIG_DIR"] + "config", "r") as file:
        content = file.read()
        content = content.split()
        if not "[extension]" in content:
            raise RuntimeError("the extensions dir is not setup correctly. Please rerun setup")
        indexOfExtensions = content.index("[extension]")
        if not indexOfExtensions or len(content) <= indexOfExtensions + 1:
            raise RuntimeError("the extensions dir is not setup correctly. Please rerun setup")
        if not os.path(content[indexOfExtensions + 1]):
            raise RuntimeError("the path to the cli extensions does not exist"
                              " try running setup again with a valid extensions dir")
        os.environ["AZURE_EXTENSION_DIR"] = content[indexOfExtensions + 1]


def runTest(testToRun, live, pytestargs):
    if live: 
       os.environ[ENV_VAR_TEST_LIVE] = 'True'
    if pytestargs == "--default":
       arguments = ['-p', 'no:warnings', '--no-print-logs']
       arguments += ['-n', 'auto']
    else:
        for i in pytestargs:
           arguments += pytestargs[i].split()

    for i in testToRun: #['logic', 'portal']
        arguments
        cmd = 'python -m pytest {}'.format(' '.join(arguments))
        subprocess.call(cmd.split(), env=os.environ.copy(), shell=True)
        # clean up all test stuff
   
  
