import bpy

import os
from pathlib import Path


def initGlobalVariables():

    # icons ############
    global icons_col

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    icons_col = pcoll

    global uasDebug

    if "UasDebug" in os.environ.keys():
        uasDebug = bool(int(os.environ["UasDebug"]))
    else:
        uasDebug = False

    print("UAS debug: ", uasDebug)


def releaseGlobalVariables():

    global icons_col

    bpy.utils.previews.remove(icons_col)
    icons_col = None
