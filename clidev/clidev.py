import os
import sys
import subprocess
import shutil
import argparse
from clidev import utils
import clidev as cli


def setupConfig(args):

    pathToCliExtensionRepo = args.path
    if args.set_evn:
        subprocess.call(cli.VENV_CMD + args.set_evn,
                        shell=True)  # windows only for now
        azureConfigPath = os.path.join(os.path.abspath(os.getcwd()),
                                       args.set_evn)
    elif os.environ.get(cli.VIRTUAL_ENV):
        azureConfigPath = os.environ.get(cli.VIRTUAL_ENV)
    else:
        raise RuntimeError("You are not running inside a virtual enviromet and have not specfied "
                           "to create one")

    dotAzureConfig = os.path.join(azureConfigPath, '.azure')
    if os.path.isdir(dotAzureConfig):
        shutil.rmtree(dotAzureConfig)
    globalAzConfig = os.path.expanduser(os.path.join('~', '.azure'))
    config = os.path.join(dotAzureConfig, cli.CONFIG_NAME)
    if os.path.isdir(os.path.join(globalAzConfig)) and args.copy:
        print("\ncopying " + str(globalAzConfig) + " to " + str(dotAzureConfig))
        shutil.copytree(globalAzConfig, dotAzureConfig)
    else:
        os.mkdir(dotAzureConfig)
        file = open(config, "w")
        file.close()

    content = open(config, "r").readlines()
    file = open(config, "w")
    if cli.CLOUD_TAG not in content:
        content += [cli.CLOUD_TAG, "name = " + cli.AZ_CLOUD + "\n"]
    if cli.EXTENSION_TAG not in content:
        content += [cli.EXTENSION_TAG,
                    "dev_sources = " + pathToCliExtensionRepo + "\n"]
    else:
        content[content.index(cli.EXTENSION_TAG) + 1] = "dev_sources = " + \
            pathToCliExtensionRepo + "\n"
    file.writelines(content)
    file.close()

    # only for powershell for now
    activatePath = os.path.join(azureConfigPath, cli.SCRIPTS,
                                cli.ACTIVATE_PS)
    content = open(activatePath, "r").read()
    idx = content.find(cli.PS1_VENV_SET)
    if idx < 0:
        raise RuntimeError("hmm, it looks like " + cli.ACTIVATE_PS + " does"
                           " not set the virutal enviroment variable VIRTUAL_ENV")
    if content.find(cli.EVN_AZ_CONFIG) < 0:
        content = content[:idx] + cli.EVN_AZ_CONFIG + " = " + \
            "\"" + dotAzureConfig + "\"; " + \
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

    if not os.environ.get(cli.VIRTUAL_ENV):
        raise RuntimeError("You are not running inside a virtual enviromet")
    if not os.environ.get(cli.AZ_CONFIG_DIR):
        raise RuntimeError(
            "AZURE_CONFIG_DIR env var is not set. Please rerun setup")
    if not os.path.exists(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config")):
        raise RuntimeError(
            "The Azure config file does not exist. please rerun setup")
    with open(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config"), "r") as file:
        content = file.read()
        content = content.split()
        os.environ["AZURE_EXTENSION_DIR"] = utils.validateConfig(content)
        runTest(args.test, args.live, args.options, args.all, args.clean)


def runTest(testToRun, live, pyArgs, all, clean):

    if live:
        os.environ['AZURE_TEST_RUN_LIVE'] = 'True'
    arguments = ['-p', 'no:warnings'] if not pyArgs else pyArgs
    arguments = arguments[1:-1].split() if (arguments[0] +
                                            arguments[-1] == '[]') else arguments
    baseExtensionsPath = os.path.join(os.environ["AZURE_EXTENSION_DIR"], 'src')

    # Change dir to root of extension so all test that use files pass
    # All test should use path from the root for their test files
    os.chdir(os.environ["AZURE_EXTENSION_DIR"])
    for i in testToRun:
        testPath = os.path.join(baseExtensionsPath, i)
        cmd = ("python " + ('-B ' if clean else '') +
               "-m pytest {}").format(' '.join([testPath] + arguments))
        print("cmd being run is: " + str(cmd))
        subprocess.call(cmd.split(), env=os.environ.copy(), shell=True)
        if not live and clean:
            recordings = os.path.join(testPath,
                                      cli.AZEX_PREFIX + i,
                                      'tests',
                                      'latest',
                                      'recordings')
            if os.path.isdir(recordings):
                recordingFiles = os.listdir(recordings)
                [os.remove(os.path.join(recordings, file))
                 for file in recordingFiles if file.endswith(".yaml")]

def main():
    parser = argparse.ArgumentParser(prog='clidev')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    # setup parser
    parserSetup = subparsers.add_parser(
        'setup', aliases=['s'], help='setup help')
    parserSetup.add_argument(
        "path", type=str, help="Path to cli-extensions repo")
    parserSetup.add_argument('-s', '--set-evn', type=str, help="Will " +
                             "create a virtual enviroment with the given evn name")
    parserSetup.add_argument('-c', '--copy', action='store_true', help="copy entire global" +
                             " .azure diretory to the newly created virtual enviroment .azure direcotry" +
                             " if it exist")
    parserSetup.set_defaults(func=setupConfig)

    # test parse
    parserTest = subparsers.add_parser('test', aliases=['t'], help='test help')
    parserTest.add_argument('--options', type=str, help="A string represention of pytest args surrounded by \"[]\"." +
                            " Example: --options \"[-s -l --tb=auto]\"")
    parserTest.add_argument(
        '--live', action='store_true', help='Run test live')
    parserTest.add_argument('--clean', action='store_true',
                            help='Will clean up cache always if selected and will clean recordings if live is not selected.')
    group = parserTest.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='Run all cli-extensions tests')
    group.add_argument('-t', '--test', nargs='+', help='List of test to run')
    parserTest.set_defaults(func=setupTestEnv)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)
    
if __name__ == "__main__":
    main()
