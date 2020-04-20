from clidev.constants import AZ_DEV_SRC
import os

def validateConfig(content):
    indexOfExtensions = content.index("[extension]")
    if (indexOfExtensions < 0 or len(content) <= indexOfExtensions + 2 or 
        content[indexOfExtensions + 1] != AZ_DEV_SRC or
        content[indexOfExtensions + 2] != '='):
        raise RuntimeError("the extensions dir is not setup correctly. Please rerun setup")
    if not os.path.isdir(content[indexOfExtensions + 3]):
        raise RuntimeError("the path to the cli extensions does not exist"
                        " try running setup again with a valid extensions dir")
    return content[indexOfExtensions + 3]