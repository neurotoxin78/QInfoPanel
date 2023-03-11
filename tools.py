import sys
import toml
from os import listdir


def get_config():
    return toml.load("config.toml")


def extended_exception_hook(exec_type, value, traceback):
    # Print the error and traceback
    con.log(exec_type, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exec_type, value, traceback)
    sys.exit(1)


def get_apps_list(path):
    return listdir(path)


def loadStylesheet(sshFile):
    with open(sshFile, "r") as fh:
        return fh.read()


def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]