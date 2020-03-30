import os
import sys
import subprocess

if __name__ == "__main__":
    pass

def setupUpConfig(pathToCliExtensionRepo):
    # first cut, need to check if dirs already exist and files already
    # exist. Parse those files to see if things are already setup etc
    if not os.environ.get('VIRTUAL_ENV'):
        raise RuntimeError("you are not running inside a virtual enviromet or VIRTUAL_ENV is not set")
    os.environ["AZURE_CONFIG_DIR"] = os.environ.get('VIRTUAL_ENV')
    with open(os.environ["AZURE_CONFIG_DIR"] + "config", "w+") as file:
        file.write("[extension]\n")
        file.write("dev_sources = " + pathToCliExtensionRepo)
    

def setupTestEnv():
    if not os.environ.get("AZURE_CONFIG_DIR"):
        raise RuntimeError("AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    with open(os.environ["AZURE_CONFIG_DIR"] + "config", "r") as file:
        content = file.read()
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
       pytestargs = pytestargs.split()
       if "io" in pytestargs:
           if pytestargs[pytestargs.index('io') + 1].lower() == 'true':
               arguments.append('-s')
             
   cmd = 'python -m pytest {}'.format(' '.join(arguments))
   subprocess.call(cmd.split(), shell=True)
   
  
