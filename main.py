from settings import *
from gui import *
from photo_resizing import batch_edit

from pi_heif import register_heif_opener

register_heif_opener()



def processImages(selectedFiles: list):
    print(selectedFiles)
    configFilePath = Path.cwd() / "resizer.ini"
    configObject = configparser.ConfigParser()
    configObject.read(configFilePath)
    saveLocation = Path(configObject["cookies"]["working directory"]) / "resizer"

    if not(saveLocation.is_dir()):
        saveLocation.mkdir()

    newDim = tuple(map(int, configObject["settings"]["targetDim"].split("x")))
    newSize = float(configObject["settings"]["downsize %"])
    doCollage = bool(int(configObject["settings"]["collage"]))

    imageFiles = selectedFiles

    if not(imageFiles):
        allFiles = Path(configObject["cookies"]["working directory"]).glob("*.*")
        imageFiles = list(e for e in allFiles if e.suffix.lower() in [".png", ".jpg", ".jpeg", ".heic"])

    batch_edit(imageFiles, saveLocation, newDim, newSize, doCollage)


def main():

    checkConfig()

    spawnWindow()

    tk.mainloop()


if __name__ == '__main__':
    main()