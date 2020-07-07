import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


def convertVersionStrToInt(versionStr):
    """ Convert a string formated like "1.23.48" to a version integer such as 1023048
    """
    formatedVersion = "{:02}{:03}{:03}"
    versionSplitted = versionStr.split(".")
    return int(formatedVersion.format(int(versionSplitted[0]), int(versionSplitted[1]), int(versionSplitted[2])))


def convertVersionIntToStr(versionInt):
    """ Convert an integer formated like 1023048 to a version string such as "1.23.48"
    """
    versionIntStr = str(versionInt)
    length = len(versionIntStr)
    versionStr = (
        str(int(versionIntStr[-1 * length : length - 6]))
        + "."
        + str(int(versionIntStr[-6 : length - 3]))
        + "."
        + str(int(versionIntStr[-3:length]))
    )
    return versionStr


def addonVersion(addonName):
    """ Return the add-on version in the form of a tupple made by: 
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
    """
    import addon_utils

    #   print("addonVersion called...")
    versionStr = "-"
    versionTupple = [
        addon.bl_info.get("version", (-1, -1, -1))
        for addon in addon_utils.modules()
        if addon.bl_info["name"] == addonName
    ]
    if len(versionTupple):
        versionTupple = versionTupple[0]
        versionStr = str(versionTupple[0]) + "." + str(versionTupple[1]) + "." + str(versionTupple[2])

        # versionStr = "131.258.265"
        versionInt = convertVersionStrToInt(versionStr)

        # print("versionStr: ", versionStr)
        # print("versionInt: ", versionInt)
        # print("convertVersionIntToStr: ", convertVersionIntToStr(versionInt))

    return (versionStr, versionInt)


class PropertyRestoreCtx:
    """
    Restore property values at the end of the block.

    """

    def __init__(self, *properties):
        self.backups = None
        self.props = properties

    def __enter__(self):
        self.backups = list()
        for p in self.props:
            try:
                self.backups.append((p[0], p[1], getattr(p[0], p[1])))
            except AttributeError:
                continue

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.backups:
            setattr(p[0], p[1], p[2])


class UAS_ShotManager_OpenExplorer(Operator):
    bl_idname = "uas_shot_manager.render_openexplorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory"

    path: StringProperty()

    def execute(self, context):
        pathToOpen = self.path
        absPathToOpen = bpy.path.abspath(pathToOpen)
        head, tail = os.path.split(absPathToOpen)
        # wkip pouvoir ouvrir path relatif
        absPathToOpen = head + "\\"

        if Path(absPathToOpen).exists():
            subprocess.Popen(f'explorer "{absPathToOpen}"')
        else:
            print('Open Explorer failed: Path not found: "' + absPathToOpen + '"')

        return {"FINISHED"}


def ShowMessageBox(message="", title="Message Box", icon="INFO"):
    """
        # #Shows a message box with a specific message 
        # ShowMessageBox("This is a message") 

        # #Shows a message box with a message and custom title
        # ShowMessageBox("This is a message", "This is a custom title")

        # #Shows a message box with a message, custom title, and a specific icon
        # ShowMessageBox("This is a message", "This is a custom title", 'ERROR')
    """

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# #Shows a message box with a specific message
# ShowMessageBox("This is a message")

# #Shows a message box with a message and custom title
# ShowMessageBox("This is a message", "This is a custom title")

# #Shows a message box with a message, custom title, and a specific icon
# ShowMessageBox("This is a message", "This is a custom title", 'ERROR')


def file_path_from_uri(uri):
    path = unquote_plus(urlparse(uri).path).replace("\\", "//")
    if re.match(r"^/\S:.*", path):  # Remove leading /
        path = path[1:]

    return path


def add_background_video_to_cam(
    camera: bpy.types.Camera, movie_path, frame_start, alpha=-1, proxyRenderSize="PROXY_50"
):
    """ Camera argument: use camera.data, not the camera object
        proxyRenderSize is PROXY_25, PROXY_50, PROXY_75, PROXY_100, FULL
    """
    print("add_background_video_to_cam")
    movie_path = Path(movie_path)
    if not movie_path.exists():
        print("    Invalid media path: ", movie_path)
        return

    if "FINISHED" in bpy.ops.clip.open(directory=str(movie_path.parent), files=[{"name": movie_path.name}]):
        print("   Finished block")
        clip = bpy.data.movieclips[movie_path.name]
        clip.frame_start = frame_start
        camera.show_background_images = True
        bg = camera.background_images.new()
        bg.source = "MOVIE_CLIP"
        bg.clip = clip
        print("   bg.clip.name:", bg.clip.name)

        bg.display_depth = "FRONT"
        bg.frame_method = "CROP"
        if -1 != alpha:
            bg.alpha = alpha

        bg.clip_user.proxy_render_size = proxyRenderSize


class UAS_Utils_RunScript(Operator):
    bl_idname = "uas_utils.run_script"
    bl_label = "Run Script"
    bl_description = "Open a script and run it"

    path: StringProperty()

    def execute(self, context):
        import pathlib

        myPath = str(pathlib.Path(__file__).parent.absolute()) + "\..\\api\\api_first_steps.py"
        print("\n*** UAS_Utils_RunScript Op is running: ", myPath)
        bpy.ops.script.python_file_run(filepath=bpy.path.abspath(myPath))
        return {"FINISHED"}


def findFirstUniqueName(originalItem, name, itemsArray):
    """ Return a string that correspont to name.xxx as the first unique name in the array
    """
    itemInd = 0
    numDuplicatesFound = 0
    newIndexStr = ".{:03}"
    newName = name
    while itemInd < len(itemsArray):
        if itemsArray[itemInd] != originalItem and newName == itemsArray[itemInd].name:
            newName = name + newIndexStr.format(numDuplicatesFound)
            numDuplicatesFound += 1
            itemInd = 0
        else:
            itemInd += 1

    return newName


_classes = (
    UAS_ShotManager_OpenExplorer,
    UAS_Utils_RunScript,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
