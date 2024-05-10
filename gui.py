import tkinter as tk
import tkinter.filedialog
from settings import *
from main import processImages

import pyautogui

def spawnWindow():

    selectedFiles = []
    root = tk.Tk()
    root.title("Resizer")
    root.config(bg='skyblue')
    configState = getSettings()

    directoryWidgets = tk.Frame(master=root, relief=tk.RIDGE, height=100, bg='grey', padx=5, pady=2)
    configWidgets = tk.Frame(master=root, relief=tk.RIDGE, width=200, height=200, bg='grey', padx=5, pady=2)
    goWidgets = tk.Frame(master=root, relief=tk.RIDGE, width=100, height=90, bg='grey', padx=5, pady=2)

    outdir = tk.Button(master=directoryWidgets)
    wkdir = tk.Button(master=directoryWidgets,
                      text=f'Working Directory: {getWorkingDir()}',
                      width=20,
                      anchor="e",
                      command=lambda: getNewDirectory() or wkdir.config(text=str(getWorkingDir())) or outdir.config(text=str(getoutdir())))
    wkdir.grid(row=0, column=0)
    outdir.config(text=f'Output Directory: {getoutdir()}', width=20, anchor="e")
    outdir.grid(row=1, column=0)

    fileSelector = tk.Button(master=directoryWidgets,
                             text="Select Files",
                             command=lambda: selectNewFiles(selectedFiles))
    fileSelector.grid(row=0, column=1)
    fileDeselector = tk.Button(master=directoryWidgets,
                             text="Deselect Files",
                             command=lambda: deselectAllFiles(selectedFiles))
    fileDeselector.grid(row=1, column=1)

    curRow = 0

    entryWidgets = []
    for parameter in configState.keys():
        # if list(configState.keys()).index(parameter) == 0: continue
        label = tk.Label(master=configWidgets, text=parameter)
        label.grid(row=curRow, column=0)
        entry = tk.Entry(master=configWidgets, width=4)
        entry.grid(row=curRow, column=1)
        entry.insert(0, configState[parameter])
        entryWidgets.append((parameter, entry))
        curRow += 1



    goButton = tk.Button(goWidgets, text="Apply", bg="slateblue", command=lambda: processImages(selectedFiles))
    goButton.grid(row=0, column=0)

    root.bind('<Return>', lambda event: updateEntryWidgets(entryWidgets))

    configWidgets.grid(row=1, column=0, padx=10, pady=5, ipady=2, ipadx=5)
    goWidgets.grid(row=1, column=1)
    directoryWidgets.grid(row=0, column=0, columnspan=2, padx=10, pady=5, ipady=2, ipadx=5)

def size_window(win):
    height = win.winfo_screenheight() / 2
    width = win.winfo_screenwidth() / 2
    win.geometry("%dx%d" % (width, height))

def selectNewFiles(selectedFiles: list):
    selectedFiles.clear()
    selectedFiles += tk.filedialog.askopenfilenames(initialdir=r"C:\Users\tysin\OneDrive\Pictures",
                                                    title="Choose photos to resizer",
                                                    filetypes=[
                                                        ("Image files", "*.jpg *.jpeg *.png *.gif *.tiff *.heic"),
                                                        ("All files", "*.*")]
                                                    )
def deselectAllFiles(selectedFiles: list):
    selectedFiles = []

def getNewDirectory():
    newDir = tk.filedialog.askdirectory(initialdir=getWorkingDir(),
                               title="Choose a directory to work from")
    if not(newDir==""):
        updateConfig("working directory", newDir, "cookies")

def updateEntryWidgets(widgets: list):
    for pair in widgets:
        param = pair[0]
        val =  pair[1].get()
        updateConfig(param, val)
        print(f"{param}: {val}")


