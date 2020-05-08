import os
import sys
import subprocess
import shutil
import argparse
from clidev import utils
from clidev.config import Config
import clidev as cli
import shlex


def setup_config(args):

    if args.set_evn:
        subprocess.call(shlex.split((cli.VENV_CMD if cli.IS_WINDOWS else cli.VENV_CMD3) + args.set_evn),
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


def setup_test_env(args):
    # this will setup pytest for CLI extension to run
    # in a clean enviroment. It will allow the user to customize
    # pytest commands or use a default set of pytest commands
    # it will also clean up the test enviroment unless the user specifies
    # otherwise
    utils.validate_env()
    config = Config(os.path.join(
        os.environ[cli.AZ_CONFIG_DIR], "config"))
    if cli.EXT_SECTION not in config or cli.AZ_DEV_SRC not in config[cli.EXT_SECTION]:
        raise RuntimeError(
            "no extension section or dev_sources specified in the config")
    run_test(args.test, args.live, args.options, args.all, args.clean, config)


def run_test(test_to_run, live, py_args, all, clean, config):

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
        print("cmd being run is: " + str(cmd.split))
        subprocess.call(cmd.split(), env=os.environ.copy(), shell=False)
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


def gen_extension(args):

    utils.validate_env()
    # construct and validate cli-extensions repo path and swagger readme file path
    config = Config(os.path.join(os.environ[cli.AZ_CONFIG_DIR], "config"))
    extensions_repo_path = os.path.join(
        config[cli.EXT_SECTION][cli.AZ_DEV_SRC])
    swagger_repo_path = os.path.abspath(args.swagger_repo_path)
    swagger_readme_file_path = os.path.join(
        swagger_repo_path, 'specification', args.extension_name, 'resource-manager')
    print("\n======================================================================")
    print("cli-extensions repo path:\n" + str(extensions_repo_path))
    print("RP's readme file path in azure-rest-api-specs:\n" +
          str(swagger_readme_file_path))
    if not os.path.isdir(extensions_repo_path):
        raise RuntimeError(args.extension_name + " does not exist")
    if not os.path.isdir(swagger_readme_file_path):
        raise RuntimeError(swagger_readme_file_path + " does not exist")
    print("======================================================================\n")

    print("start generating extension " + str(args.extension_name))
    # install autorest
    subprocess.check_output('npm install -g autorest', shell=True)
    # update autorest core
    subprocess.check_output('autorest --latest', shell=True)
    cmd = cli.AUTO_REST_CMD + \
        str(extensions_repo_path) + ' ' + str(swagger_readme_file_path)
    subprocess.call(cmd, shell=True)


def add_extension(args):
    utils.validate_env()
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
    parser_setup = subparsers.add_parser(
        'setup', aliases=['s'], help='setup help')
    parser_setup.add_argument(
        "path", type=str, help="Path to cli-extensions repo")
    parser_setup.add_argument('-cli', '--cli-path',
                              type=str, help="Path to cli repo which will be installed")
    parser_setup.add_argument('-s', '--set-evn', type=str, help="Will " +
                              "create a virtual enviroment with the given evn name")
    parser_subgroup = parser_setup.add_mutually_exclusive_group(required=False)
    parser_subgroup.add_argument('-c', '--copy', action='store_true', help="copy entire global" +
                                 " .azure diretory to the newly created virtual enviroment .azure direcotry" +
                                 " if it exist")
    parser_subgroup.add_argument('-g', '--use-global', action='store_true',
                                 help="will use the default global system .azure config")
    parser_setup.set_defaults(func=setup_config)

    # test parser
    parser_test = subparsers.add_parser(
        'test', aliases=['t'], help='test help')
    parser_test.add_argument('--options', type=str, help="A string represention of pytest args surrounded by \"[]\"." +
                             " Example: --options \"[-s -l --tb=auto]\"")
    parser_test.add_argument(
        '--live', action='store_true', help='Run test live')
    parser_test.add_argument('--clean', action='store_true',
                             help='Will clean up cache always if selected and will clean recordings if live is not selected.')
    group = parser_test.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='Run all cli-extensions tests')
    group.add_argument('-t', '--test', nargs='+', help='List of test to run')
    parser_test.set_defaults(func=setup_test_env)

    # generate extension parser
    parser_gen_extension = subparsers.add_parser(
        'generate', aliases=['g'], help='generate an extension')
    parser_gen_extension.add_argument(
        'extension_name', type=str, help='Extension name')
    parser_gen_extension.add_argument(
        'swagger_repo_path', type=str, help='Path to azure-rest-api-specs repo')
    parser_gen_extension.set_defaults(func=gen_extension)

    # add extension parser
    parser_extensions = subparsers.add_parser(
        'add', aliases=['a'], help='add an extensions')
    parser_extensions.add_argument(
        "extension_name", type=str, help="Extension name")
    parser_extensions.set_defaults(func=add_extension)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
