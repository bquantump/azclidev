import os
import sys
import subprocess
import shutil
import argparse
from clidev import utils
from clidev.config import Config
import clidev as cli
import shlex


def setupConfig(args):

    if args.set_evn:
        subprocess.call(shlex.split(cli.VENV_CMD + args.set_evn),
                        shell=False)  
        azure_config_path = os.path.join(os.path.abspath(os.getcwd()),
                                         args.set_evn)
    elif os.environ.get(cli.VIRTUAL_ENV):
        azure_config_path = os.environ.get(cli.VIRTUAL_ENV)
    else:
        raise RuntimeError("You are not running inside a virtual enviromet and have not specfied "
                           "to create one")

    dot_azure_config = os.path.join(azure_config_path, '.azure')
    if os.path.isdir(dot_azure_config):
        shutil.rmtree(dot_azure_config)
    global_az_config = os.path.expanduser(os.path.join('~', '.azure'))
    config_path = os.path.join(dot_azure_config, cli.CONFIG_NAME)
    if os.path.isdir(global_az_config) and args.copy:
        shutil.copytree(global_az_config, dot_azure_config)
    elif not args.use_global:
        os.mkdir(dot_azure_config)
        file = open(config_path, "w")
        file.close()
    elif os.path.isdir(global_az_config):
        dot_azure_config = global_az_config
        config_path = os.path.join(dot_azure_config, cli.CONFIG_NAME)
    else:
        raise RuntimeError(
            "Global AZ config is not set up, yet it was specified to be used.")

    config = Config(config_path)
    if cli.CLOUD_SECTION not in config:
        config[cli.CLOUD_SECTION] = cli.AZ_CLOUD
    path_to_cli_extension_repo = os.path.abspath(args.path)
    config[cli.EXT_SECTION] = {cli.AZ_DEV_SRC: path_to_cli_extension_repo}
    if args.cli_path:
        config[cli.CLI_SECTION] = {
            cli.AZ_DEV_SRC: os.path.abspath(args.cli_path)}
    config.write()

    utils.edit_activate(azure_config_path, dot_azure_config)
    
    if args.cli_path:
        utils.install_cli(os.path.abspath(args.cli_path), azure_config_path)

    print("\n======================================================================")
    print("The setup was successful. Please run or re-run the virtual\n" +
          "environment activation script (either activate or activate.ps1)\n")
    print("======================================================================\n")


def setupTestEnv(args):
    # this will setup pytest for CLI extension to run
    # in a clean enviroment. It will allow the user to customize
    # pytest commands or use a default set of pytest commands
    # it will also clean up the test enviroment unless the user specifies
    # otherwise
    utils.validateEnv()
    config = Config(os.path.join(
        os.environ[cli.AZ_CONFIG_DIR], "config"))
    if cli.EXT_SECTION not in config or cli.AZ_DEV_SRC not in config[cli.EXT_SECTION]:
        raise RuntimeError(
            "no extension section or dev_sources specified in the config")
    runTest(args.test, args.live, args.options, args.all, args.clean, config)



def runTest(test_to_run, live, py_args, all, clean, config):

    if live:
        os.environ['AZURE_TEST_RUN_LIVE'] = 'True'
    arguments = ['-p', 'no:warnings'] if not py_args else py_args
    arguments = arguments[1:-1].split() if (arguments[0] +
                                            arguments[-1] == '[]') else arguments
    base_extensions_path = os.path.join(
        config[cli.EXT_SECTION][cli.AZ_DEV_SRC], 'src')

    # Change dir to root of extension so all test that use files pass
    # All test should use path from the root for their test files
    os.chdir(config[cli.EXT_SECTION][cli.AZ_DEV_SRC])
    for i in test_to_run:
        testPath = os.path.join(base_extensions_path, i)
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
                recording_files = os.listdir(recordings)
                [os.remove(os.path.join(recordings, file))
                 for file in recording_files if file.endswith(".yaml")]


def addExtension(args):
    utils.validateEnv()
    config = Config(os.path.join(
        os.environ[cli.AZ_CONFIG_DIR], "config"))
    extensions_path = os.path.join(
        config[cli.EXT_SECTION][cli.AZ_DEV_SRC], 'src', args.extension_name)
    print("here extension is " + str(extensions_path))
    if os.path.isdir(extensions_path):
        os.chdir(extensions_path)
        subprocess.call(cli.INSTALL_EXT_CMD, shell=True)
    else:
        raise RuntimeError(args.extension_name + " doest not exist")


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
    parserSetup.add_argument('-cli', '--cli-path',
                             type=str, help="Path to cli repo which will be installed")
    parserSetup.add_argument('-s', '--set-evn', type=str, help="Will " +
                             "create a virtual enviroment with the given evn name")
    parserSubGroup = parserSetup.add_mutually_exclusive_group(required=False)
    parserSubGroup.add_argument('-c', '--copy', action='store_true', help="copy entire global" +
                                " .azure diretory to the newly created virtual enviroment .azure direcotry" +
                                " if it exist")
    parserSubGroup.add_argument('-g', '--use-global', action='store_true',
                                help="will use the default global system .azure config")
    parserSetup.set_defaults(func=setupConfig)

    # test parser
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

    # add extension parser
    parserExtensions = subparsers.add_parser(
        'add', aliases=['t'], help='add an extensions')
    parserExtensions.add_argument(
        "extension_name", type=str, help="Extension name")
    parserExtensions.set_defaults(func=addExtension)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
