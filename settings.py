from pathlib import Path
import configparser

def updateConfig(parameterName, newValue, sectionName="settings"):

    configFilePath = Path.cwd() / "resizer.ini"

    configObject = configparser.ConfigParser()

    configObject.read(configFilePath)

    configSection = configObject[sectionName]
    configSection[parameterName] = newValue

    #configObject[sectionName] = configSection
    with open(configFilePath, "w") as fp:
        configObject.write(fp)

    return

def getSettings() -> dict:
    configFilePath = Path.cwd() / "resizer.ini"
    configObject = configparser.ConfigParser()
    configObject.read(configFilePath)
    return dict(configObject["settings"])


def getWorkingDir():
    configFilePath = Path.cwd() / "resizer.ini"
    configObject = configparser.ConfigParser()
    configObject.read(configFilePath)
    return Path(configObject["cookies"]["working directory"])


def getoutdir():
    return getWorkingDir() / "resizer\\"


def checkConfig():
    configFilePath = Path.cwd() / "resizer.ini"
    if not(configFilePath.is_file()):
        configObject = configparser.ConfigParser()
        configObject["settings"] = {
            'targetDim': "4x6",
            'collage': False,
            'Downsize %': 100

        }

        configObject["cookies"] = {
            'working directory': r"C:\Users\tysin\OneDrive\Pictures"
        }

        with open(configFilePath, "w") as fp:
            configObject.write(fp)