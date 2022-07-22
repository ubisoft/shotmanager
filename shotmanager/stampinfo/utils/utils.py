# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
functions that are not particularly related to the add-on and that could be reused as is
"""

import sys
import re
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

import bpy

import os

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def convertVersionStrToInt(versionStr):
    """Convert a string formated like "1.23.48" to a version integer such as 1023048
    Any text or space placed before the first digit is ignored
    """
    formatedVersion = "{:02}{:03}{:03}"
    firstDigitInd = 0
    for i, c in enumerate(versionStr):
        if c.isdigit():
            firstDigitInd = i
            break
    versionStr = versionStr[firstDigitInd:]
    versionSplitted = versionStr.split(".")
    return int(formatedVersion.format(int(versionSplitted[0]), int(versionSplitted[1]), int(versionSplitted[2])))


def convertVersionIntToStr(versionInt):
    """Convert an integer formated like 1023048 to a version string such as "1.23.48" """
    if versionInt < 1000000:
        versionInt = 1000000
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
    """Return the add-on version in the form of a tupple made by:
        - a string x.y.z (eg: "1.21.3")
        - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
    Return None if the addon has not been found
    """
    import addon_utils

    #   print("addonVersion called...")
    versionStr = "-"
    versionInt = -1
    versions = None

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

        versions = (versionStr, versionInt)

    return versions


def display_addon_registered_version(addon_name, more_info=""):
    versionTupple = addonVersion(addon_name)
    if versionTupple is not None:
        print(
            "\n*** *** Registering Ubisoft "
            + addon_name
            + " Add-on - version: "
            + versionTupple[0]
            + f"  ({versionTupple[1]})"
            + (f" - {more_info}" if more_info != "" else "")
            + " *** ***"
        )
    else:
        print('\n *** Cannot find registered version for add-on "' + addon_name + '" ***\n')
    return versionTupple


def addonCategory(addonName):
    import addon_utils

    categ = ""
    for addon in addon_utils.modules():
        if addon.bl_info["name"] == addonName:
            categ = addon.bl_info["category"]
    return categ


# To get the script path folder use this:
# https://blender.stackexchange.com/questions/64129/get-blender-scripts-path
# bpy.utils.script_paths()
# or bpy.utils.script_path_user()


def addonPath():
    "Return the install path of this add-on"
    # get the path of this file and climb to its parent
    filePath = Path(os.path.dirname(os.path.abspath(__file__))).parent
    return str(filePath)


def getPythonPackagesFolder():
    pyExeFile = sys.executable
    # we have to go above \bin dir
    localPyDir = str((Path(pyExeFile).parent).parent) + "\\lib\\site-packages\\"
    return localPyDir


def file_path_from_uri(uri):
    path = unquote_plus(urlparse(uri).path).replace("\\", "//")
    if re.match(r"^/\S:.*", path):  # Remove leading /
        path = path[1:]

    return path


def openMedia(media_filepath, inExternalPlayer=False):
    if not Path(media_filepath).exists():
        print(f"*** Cannot open {media_filepath}")
        return

    if inExternalPlayer:

        # wkip subprocess is said to be better but cannot make it work...
        # import subprocess
        #  p = subprocess.Popen(["display", media_filepath])
        # subprocess.run(["open", media_filepath], check=True)

        import subprocess
        import os
        import platform

        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", media_filepath))
        elif platform.system() == "Windows":  # Windows
            os.startfile(media_filepath)
        else:  # linux variants
            subprocess.call(("xdg-open", media_filepath))
    else:
        # Call user prefs window
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        # Change area type
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = "IMAGE_EDITOR"

        # bpy.ops.render.view_show()
        bpy.ops.image.open(
            filepath=media_filepath,
            relative_path=False,
            show_multiview=False,
        )

        # bpy.data.images.[image_name].reload()

        #  print(f"media_filepath: {media_filepath}")
        #  print(f"Path(media_filepath).name: {Path(media_filepath).name}")
        myImg = bpy.data.images[Path(media_filepath).name]
        #  print("myImg:" + str(myImg))
        bpy.context.area.spaces.active.image = myImg

    return


def add_background_video_to_cam(
    camera: bpy.types.Camera, movie_path, frame_start, alpha=-1, proxyRenderSize="PROXY_50"
):
    """Camera argument: use camera.data, not the camera object
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


###################
# Render
###################


def convertToSupportedRenderResolution(res):
    """Return an array of int where the provided render resolution has been converted to multiples of 2
    Args:
        res:    array [w, h]"""
    validRes_w = int(res[0])
    if 0 != validRes_w % 2:
        validRes_w += 1
    validRes_h = int(res[1])
    if 0 != validRes_h % 2:
        validRes_h += 1
    return [validRes_w, validRes_h]


###################
# Various
###################


def findFirstUniqueName(originalItem, name, itemsArray):
    """Return a string that correspont to name.xxx as the first unique name in the array"""
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


def getSceneVSE(vsm_sceneName, createVseTab=False):
    """Return the scene that has the name held by vsm_sceneName and adds a VSE in it if there is not already one.
    Use <returned scene>.sequence_editor to get the vse of the scene
    """
    vsm_scene = None

    if vsm_sceneName in bpy.data.scenes:
        vsm_scene = bpy.data.scenes[vsm_sceneName]
    else:
        vsm_scene = bpy.data.scenes.new(name=vsm_sceneName)
        vsm_scene.render.fps = bpy.context.scene.render.fps

    if not vsm_scene.sequence_editor:
        vsm_scene.sequence_editor_create()

    bpy.context.window.scene = vsm_scene

    print(f"bpy.context.window.screen.name: {bpy.context.window.screen.name}")
    if "temp" == bpy.context.window.screen.name:
        print("pafffffffffffffffffff")
        bpy.context.window.screen = bpy.context.window_manager.windows[0].screen
        bpy.context.window.screen = bpy.data.screens["UV Editing"]
        bpy.context.window_manager.windows[1].screen = bpy.data.screens["UV Editing"]

        #     bpy.ops.wm.window_close()
    #        bpy.ops.window.remove()

    # if bpy.context.window_manager.windows[#].workspace
    bpy.context.window.scene = vsm_scene
    print(f"2bpy.context.window.workspace.name: {bpy.context.window.workspace.name}")
    print(f"2bpy.context.window.screen.name: {bpy.context.window.screen.name}")

    if createVseTab:
        startup_blend = os.path.join(
            bpy.utils.resource_path("LOCAL"),
            "scripts",
            "startup",
            "bl_app_templates_system",
            "Video_Editing",
            "startup.blend",
        )

        if "Video Editing" not in bpy.data.workspaces:
            bpy.ops.workspace.append_activate(idname="Video Editing", filepath=startup_blend)

    return vsm_scene


def duplicateObject(sourceObject):
    """Duplicate (deepcopy) an object and place it in the same collection"""
    newObject = sourceObject.copy()
    newObject.animation_data.action = sourceObject.animation_data.action.copy()
    newObject.data = sourceObject.data.copy()
    newObject.data.animation_data.action = sourceObject.data.animation_data.action.copy()

    sourceCollections = sourceObject.users_collection
    if len(sourceCollections):
        sourceCollections[0].objects.link(newObject)
    else:
        (sourceObject.users_scene)[0].collection.objects.link(newObject)
    return newObject
