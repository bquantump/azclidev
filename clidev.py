import os
import sys
import subprocess
import constants
import shutil
import argparse

def setupConfig(args):

    pathToCliExtensionRepo = args.path
    if args.set_evn:
       subprocess.call(constants.VENV_CMD + args.set_evn, 
                       shell=True) # windows only for now
       azureConfigPath = os.path.join(os.path.abspath(os.getcwd()),
                                       args.set_evn)
    elif os.environ.get(constants.VIRTUAL_ENV):
        azureConfigPath = os.environ.get(constants.VIRTUAL_ENV)
    else:
        raise RuntimeError("You are not running inside a virtual enviromet and have not specfied "
                           "to create one")
        
    dotAzureConfig = os.path.join(azureConfigPath, '.azure')
    if not os.path.isdir(dotAzureConfig):
        os.mkdir(dotAzureConfig)
    globalAzConfig = os.path.join(os.path.expanduser(os.path.join('~', '.azure')), 
                                   constants.CONFIG_NAME)
    config = os.path.join(dotAzureConfig, constants.CONFIG_NAME)
    if os.path.isfile(os.path.join(globalAzConfig)):
        shutil.copyfile(globalAzConfig, os.path.join(dotAzureConfig, 'config'))
    else:
        # create empty config file
        file = open(config, "w")
        file.close()

    content = open(config, "r").readlines()
    file = open(config, "w")
    if constants.CLOUD_TAG not in content:
        content += [constants.CLOUD_TAG, "name = " + constants.AZ_CLOUD + "\n"]
    if constants.EXTENSION_TAG not in content:
        content += [constants.CONFIG_NAME, "dev_sources = " + pathToCliExtensionRepo + "\n"]
    else:
        content[content.index(constants.EXTENSION_TAG) + 1] = "dev_sources = " + \
                                                               pathToCliExtensionRepo + "\n"
    file.writelines(content)
    file.close()
    
    # only for powershell for now
    activatePath= os.path.join(azureConfigPath, constants.SCRIPTS,
                              constants.ACTIVATE_PS)
    content = open(activatePath, "r").read()   
    idx = content.find(constants.PS1_VENV_SET)
    if idx < 0: 
        raise RuntimeError("hmm, it looks like " + constants.ACTIVATE_PS + " does"
                         " not set the virutal enviroment variable VIRTUAL_ENV")
    if content.find(constants.EVN_AZ_CONFIG) < 0:
        content = content[:idx] + constants.EVN_AZ_CONFIG + " = " + \
                                "\"" + dotAzureConfig + "\"; "  + \
                                content[idx:]
    file = open(activatePath, 'w')
    file.write(content)
    file.close()
    
    print("\n======================================================================")
    print("The setup was successful. Please run or re-run the virtual\n" +
          "environment activation script (either activate or activate.ps1)\n" +
          "Note, in future console windows you only\n" +
          "need to run the activate script and not setup again.")
    print("======================================================================\n")

def setupTestEnv(args):
    # this will setup pytest for CLI extension to run 
    # in a clean enviroment. It will allow the user to customize
    # pytest commands or use a default set of pytest commands
    # it will also clean up the test enviroment unless the user specifies 
    # otherwise
    
    if not os.environ.get(constants.VIRTUAL_ENV):
        raise RuntimeError("You are not running inside a virtual enviromet")
    if not os.environ.get(constants.AZ_CONFIG_DIR):
        raise RuntimeError("AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    with open(os.path.join(os.environ[constants.AZ_CONFIG_DIR], "config"), "r") as file:
        content = file.read()
        content = content.split()
        os.environ["AZURE_EXTENSION_DIR"] = validateConfig(content)
        runTest(args.test, args.live, args.options, args.all, args.no_clean)
        
        
    


def runTest(testToRun, live, testArgs, all, noClean):
    if live: 
       os.environ['AZURE_TEST_RUN_LIVE'] = 'True'
       
    if not testArgs:
       arguments = ['-p', 'no:warnings']
    else:
        arguments = []
        for i in testArgs:
           if i[0] != '-':
               if not arguments:
                   raise RuntimeError("invalid pytest argument " + str(i))
               arguments[-1] += " " + i
           else:
               arguments.append(i)
    baseExtensionsPath = os.path.join(os.environ["AZURE_EXTENSION_DIR"], 'src')
    for i in testToRun:
        testPath = os.path.join(baseExtensionsPath, i)
        cmd = 'python -m pytest {}'.format(' '.join([testPath] + arguments))
        print("cmd is: " + str(cmd))
        subprocess.call(cmd.split(), env=os.environ.copy(), shell=True)
        if not noClean:
            cache = os.path.join(testPath, 
                                 constants.AZEX_PREFIX,
                                 'tests',
                                 'latest')
    
def validateConfig(content):
    indexOfExtensions = content.index("[extension]")
    if (indexOfExtensions < 0 or len(content) <= indexOfExtensions + 2 or 
        content[indexOfExtensions + 1] != constants.AZ_DEV_SRC or
        content[indexOfExtensions + 2] != '='):
        raise RuntimeError("the extensions dir is not setup correctly. Please rerun setup")
    if not os.path.isdir(content[indexOfExtensions + 3]):
        raise RuntimeError("the path to the cli extensions does not exist"
                        " try running setup again with a valid extensions dir")
    return content[indexOfExtensions + 3]
    
        
if __name__ == "__main__":
    # this will parse command line arguments to trigger the correct funtions to be called
    # For example, if setup -r path is passed in, the setupConfig(path)
    
    parser = argparse.ArgumentParser(prog='clidev')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    # setup parser
    parserSetup = subparsers.add_parser('setup',aliases=['s'], help='setup help')
    parserSetup.add_argument("path", type=str, help="Path to cli-extensions repo")
    parserSetup.add_argument('-s','--set-evn', type=str, help="Will " +
                             "creat a virtual enviroment with the given evn name")
    parserSetup.set_defaults(func=setupConfig)

    # test parse
    parserTest = subparsers.add_parser('test', aliases=['t'],help='test help')
    parserTest.add_argument('--options', nargs='+', help="list of pytest options, " +
                            "if empty will use defaults options")
    parserTest.add_argument('--live', action='store_true', help='Run test live')  
    group = parserTest.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='Run all cli-extensions tests')
    group.add_argument('--no-clean', action='store_true', help='Will neither clean up cache nor recordings')  
    group.add_argument('-t','--test', nargs='+', help='List of test to run')
    parserTest.set_defaults(func=setupTestEnv)
    args = parser.parse_args()
    args.func(args)
    
