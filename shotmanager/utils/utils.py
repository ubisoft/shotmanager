# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
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
Various general purpose functions, either to manipulate scene content or code
"""

import os
import re
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import sys

from random import uniform
from xmlrpc.client import Boolean

import bpy

from shotmanager.utils import utils_os
from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def unique_object_name(obj_name):
    # TODO write new names as .00i rather than _i_i
    i = 1
    objects = bpy.data.objects
    while obj_name in objects:
        obj_name = f"{obj_name}_{i}"
        i += 1
    return obj_name


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


def isAddonLoaded(addonName):
    try:
        bpy.context.preferences.addons[addonName]
        isLoaded = True
    except Exception:
        isLoaded = False
    return isLoaded


def addonVersion(addonName):
    """Return the add-on version in the form of a tupple made by:
        - a string x.y.z (eg: "1.21.3")
        - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
    Return None if the addon has not been found
    """
    import addon_utils

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


def addonVersionFromFileName(fileName):
    """Extract the add-on version from the provided file name
    Return a tupple made by:
        - a string x.y.z (eg: "1.3.1")
        - an integer. x.y.z becomes xxyyyzzz (eg: "1.3.1" becomes 1003001)
    Return None if the addon has not been found
    Args:
        fileName:   Can be a full file path or just a file name, with a name structure such as Ubisoft_StampInfo_V1-3-1.zip
    """
    versionStr = "-"
    versionInt = -1
    versions = None

    fileNameNoExt = Path(fileName).stem
    vInd = fileNameNoExt.find("_V")
    if -1 != vInd:
        versionFileNameStr = fileNameNoExt[vInd + 2 :]
        versionDigits = versionFileNameStr.split("-")
        versionStr = str(versionDigits[0]) + "." + str(versionDigits[1]) + "." + str(versionDigits[2])
        versionInt = convertVersionStrToInt(versionStr)
        versions = (versionStr, versionInt)

    return versions


def display_addon_registered_version(addon_name, unregister=False, more_info=""):
    """Display the register or unregister message of the add-on"""
    _YELLOW = "\33[33m"
    _GRAY = "\33[1;30m"
    _WARNING = "\033[31m"
    _ENDCOLOR = "\033[0m"

    versionTupple = addonVersion(addon_name)
    if versionTupple is not None:

        textReg = "Unr" if unregister else "R"
        textColor = _GRAY if unregister else _YELLOW
        text = (
            f"\n*** *** {textReg}egistering Ubisoft "
            + addon_name
            + " Add-on - version: "
            + versionTupple[0]
            + f"  ({versionTupple[1]})"
            + (f" - {more_info}" if more_info != "" else "")
            + " *** ***"
        )
        print(f"{textColor}{text}{_ENDCOLOR}")
    else:
        print(f"{_WARNING}\n *** Cannot find registered version for add-on {addon_name} ***\n{_ENDCOLOR}")
    return versionTupple


def addonCategory(addonName):
    import addon_utils

    categ = ""
    for addon in addon_utils.modules():
        if addon.bl_info["name"] == addonName:
            categ = addon.bl_info["category"]
    return categ


def addonPath():
    "Return the install path of this add-on"
    # get the path of this file and climb to its parent
    filePath = Path(os.path.dirname(os.path.abspath(__file__))).parent
    return str(filePath)


def file_path_from_uri(uri):
    path = unquote_plus(urlparse(uri).path).replace("\\", "//")
    if re.match(r"^/\S:.*", path):  # Remove leading /
        path = path[1:]

    return path


# To get the script path folder use this:
# https://blender.stackexchange.com/questions/64129/get-blender-scripts-path
# bpy.utils.script_paths()
# or bpy.utils.script_path_user()


def getPythonPackagesFolder():
    pyExeFile = sys.executable
    # we have to go above \bin dir
    localPyDir = str((Path(pyExeFile).parent).parent) + "\\lib\\site-packages\\"
    return localPyDir


# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


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


def ShowMessageBox(message="", title="Message Box", icon="INFO"):
    """Display a message box
    A message can be drawn on several lines when containing the separator \n

    # #Shows a message box with a specific message
    # ShowMessageBox("This is a message")

    # #Shows a message box with a message and custom title
    # ShowMessageBox("This is a message", "This is a custom title")

    # #Shows a message box with a message, custom title, and a specific icon
    # ShowMessageBox("This is a message", "This is a custom title", 'ERROR')

    Icon can be "INFO" (default), "WARNING", "ERROR", "CANCEL"
    """

    messages = message.split("\n")
    blender_icon = icon
    if "WARNING" == icon:
        blender_icon = "ERROR"

    # NOTE: also possible to use return context.window_manager.invoke_props_dialog(self, width=400) in an invoke function
    def draw(self, context):
        layout = self.layout
        for s in messages:
            row = layout.row()
            if "ERROR" == blender_icon:
                row.alert = True  # doesn't seem to work with popup_menu
            row.label(text=s)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=blender_icon)


# #Shows a message box with a specific message
# ShowMessageBox("This is a message")

# #Shows a message box with a message and custom title
# ShowMessageBox("This is a message", "This is a custom title")

# #Shows a message box with a message, custom title, and a specific icon
# ShowMessageBox("This is a message", "This is a custom title", 'ERROR')


def file_path_from_url(url):
    path = ""
    if url.startswith("file"):
        path = unquote_plus(urlparse(url).path).replace("\\", "//")
    else:
        path = url.replace("\\", "/")  # //

    #  print("ulr 2 path: ", path)
    if re.match(r"^/\S:.*", path):  # Remove leading /
        path = path[1:]
    #  print("ulr 3 path: ", path)

    return path


def openMedia(media_filepath, inExternalPlayer=False):
    if not Path(media_filepath).exists():
        print(f"*** Cannot open {media_filepath}")
        return

    if inExternalPlayer:
        utils_os.open_media_in_player(media_filepath)
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
            use_sequence_detection=False,
            use_udim_detecting=False,
        )

        # bpy.data.images.[image_name].reload()

        _logger.debug_ext(f"media_filepath: {media_filepath}", col="RED")
        _logger.debug_ext(f"Path(media_filepath).name: {Path(media_filepath).name}", col="RED")
        myImg = bpy.data.images[Path(media_filepath).name]
        bpy.context.area.spaces.active.image = myImg

    return


###################
# Time
###################


def getFrameInAnimRange(scene, frame):
    """Check if the specified frame is in the current animation range of the scene
    (considering that the Preview Range can also be activated) and return a
    valid value for the frame, either the same value if in the range or one of the
    boundaries.
    """
    newFrame = frame
    if scene.use_preview_range:
        newFrame = max(newFrame, scene.frame_preview_start)
        newFrame = min(newFrame, scene.frame_preview_end)
    else:
        newFrame = max(newFrame, scene.frame_start)
        newFrame = min(newFrame, scene.frame_end)
    return newFrame


def convertFramerateToSceneFPS(framerate):
    """Set the scene fps and fps_base values
    The argument "framerate" can be a float and has to be converted because scene.render.fps is an int

    https://blenderartists.org/t/get-set-frames-per-second-in-blender/539880/3
    fps_base is the amount of time, in seconds, which is filled by fps, such that at values
    other than 1 for fps_base, fps semantically becomes “frames per base”.
    I.e. the effective framerate always is, in frames per second:
        effective fps = scene.render.fps / scene.render.fps_base

    Return a tupple made of fps (int) and fps_base (float >= 1.0)

    Usage:
        fps, fps_base = utils.convertFramerateToSceneFPS(self.project_fps)
        parentScn.render.fps = fps
        parentScn.render.fps_base = fps_base
    """

    # we assume scene.render.fps_base >= 1.0
    import math

    # scene.render.fps = int(math.ceil(project_fps))
    # scene.render.fps_base = scene.render.fps / project_fps
    fps = int(math.ceil(framerate))
    fps_base = fps / framerate

    return (fps, fps_base)


def setSceneFps(scene, framerate):
    """Apply the specified framerate to the scene by changing both scene.render.fps and scene.render.fps_base"""
    fps, fps_base = convertFramerateToSceneFPS(framerate)
    scene.render.fps = fps
    scene.render.fps_base = fps_base


def getSceneEffectiveFps(scene):
    """Return the effective scene fps, which is given by scene.render.fps / scene.render.fps_base"""
    return scene.render.fps / scene.render.fps_base


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
# Areas, Various
###################


def getAreasByType(context, area_type):
    """Return a list of the areas of the specifed type from the specified context"""
    areasList = list()
    for area in context.screen.areas:
        if area.type == area_type:
            areasList.append(area)
    return areasList


def getAreaFromIndex(context, area_index, area_type):
    """Return the area that has the index area_index in the list of areas of the specified type
    Args:
        area_type: can be "VIEW_3D", ...
    Return: None if not found
    """
    areasList = getAreasByType(context, area_type)

    if 0 <= area_index < len(areasList):
        return areasList[area_index]
    return None


def getAreaIndex(context, area, area_type):
    """Return the index of the area in the list of areas of the specified type
    *** warning: be sure area_type is really the type of area (we can get it from area.type) ***
    Args:
        area_type: can be "VIEW_3D", ...
    Return: -1 if area not found
    """
    areasList = getAreasByType(context, area_type)

    for i, a in enumerate(areasList):
        if area == a:
            return i
    return -1


def getAreaInfo(context, area, verbose=False):
    """Return a tupple with:
        - the index of the area in the list of areas of the specified type
        - the type of the area
    Args:
        area_type: can be "VIEW_3D", ...
    Return: None if area not found
    """
    if area is None:
        print(f"Specified area is nul: {i}, {area.type}")
        return None
    for i, screenArea in enumerate(context.screen.areas):
        if area == screenArea:
            if verbose:
                print(f"Area: {i}, {area.type}")
            return (i, area.type)

    return None


def setPropertyPanelContext(context, spaceContext):
    """Set the Property panel to the specified context

    Args:   spaceContext: Can be ('TOOL', 'RENDER', 'OUTPUT', 'VIEW_LAYER', 'SCENE', 'WORLD', 'OBJECT', 'MODIFIER',
            'PARTICLES', 'PHYSICS', 'CONSTRAINT', 'DATA', 'MATERIAL', 'TEXTURE')
    """
    for area in context.screen.areas:
        if area.type == "PROPERTIES":
            for space in area.spaces:
                if space.type == "PROPERTIES":
                    # specified space context is not always available (eg: no "DATA" when no objects in scene)
                    try:
                        space.context = spaceContext
                        break
                    except Exception as e:
                        _logger.debug_ext("Cannot set Properties panel to 'DATA', no such tab available", col="ORANGE")
                        _logger.debug_ext(f"{e}", col="ORANGE")


# 3D VIEW areas (= viewports)
#####################################


def getViewports(context):
    """
    Return: empty list if no viewports found
    """
    return getAreasByType(context, "VIEW_3D")


def getViewportsSpaceData(context):
    """Return a list of all the space data of all the viewports found in the current layout
    Return en empty list if no viewport exists in the screen
    """
    viewportAreas = getViewports(context)
    spaceDatas = list()
    for viewportArea in viewportAreas:
        for space_data in viewportArea.spaces:
            if "VIEW_3D" == space_data.type:
                spaceDatas.append(space_data)
    return spaceDatas


def getViewportFromIndex(context, viewport_index):
    """
    Return: None if not found
    """
    return getAreaFromIndex(context, viewport_index, "VIEW_3D")


def getViewportIndex(context, viewport):
    """
    Return: -1 if area not found
    """
    return getAreaIndex(context, viewport, "VIEW_3D")


def getCurrentViewport(context):
    """Return the area of the current viewport"""
    viewportsList = getAreasByType(context, "VIEW_3D")
    for viewportArea in viewportsList:
        if context.area == viewportArea:
            return viewportArea
    return None


def getCurrentViewportIndex(context):
    """Return the area index of the current viewport"""
    viewportsList = getAreasByType(context, "VIEW_3D")
    for ind, viewportArea in enumerate(viewportsList):
        if context.area == viewportArea:
            return ind
    return -1


# Dopesheet areas (= timelines + dopesheets + grease pencil + action + shapekey + mask + cachefile)
# cf https://docs.blender.org/api/current/bpy.types.SpaceDopeSheetEditor.html
#####################################
# DOPESHEET TIMELINE ACTION SHAPEKEY GPENCIL MASK CACHEFILE ALL


def getDopesheets(context, mode="ALL"):
    """
    Return: empty list if no dopesheets found
    """
    dopesheetAreas = getAreasByType(context, "DOPESHEET_EDITOR")
    dopesheets = list()
    for dp in dopesheetAreas:
        # wkip not sure first space is the dopesheet
        if "ALL" == mode:
            dopesheets.append(dp)
        elif dp.spaces[0].mode == mode:
            dopesheets.append(dp)

    return dopesheets


def getDopesheetFromIndex(context, dopesheet_index, mode="ALL"):
    """
    Return: None if not found
    """
    dopesheets = getDopesheets(context, mode=mode)

    if 0 <= dopesheet_index < len(dopesheets):
        return dopesheets[dopesheet_index]
    else:
        return None


def getDopesheetIndex(context, dopesheet, mode="ALL"):
    """
    Return: -1 if area not found
    """
    dopesheets = getDopesheets(context, mode=mode)
    for i, dp in enumerate(dopesheets):
        if dopesheet == dp:
            return i
    return -1


def getViewportAreaView(context, viewport_index=0):
    # for screen_area in context.screen.areas:
    #     if screen_area.type == "VIEW_3D":
    #         v3d = screen_area.spaces[0]
    #         rv3d = v3d.region_3d
    #         return rv3d

    screens3D = []
    for screen_area in context.screen.areas:
        if screen_area.type == "VIEW_3D":
            screens3D.append(screen_area)

    if len(screens3D):
        return screens3D[min(viewport_index, len(screens3D))]

    return None


########################


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
    # vsm_sceneName = "VideoShotManager"
    vsm_scene = None

    if vsm_sceneName in bpy.data.scenes:
        vsm_scene = bpy.data.scenes[vsm_sceneName]
    else:
        vsm_scene = bpy.data.scenes.new(name=vsm_sceneName)
        vsm_scene.render.fps = bpy.context.scene.render.fps
        vsm_scene.render.fps_base = bpy.context.scene.render.fps_base

    if not vsm_scene.sequence_editor:
        vsm_scene.sequence_editor_create()

    bpy.context.window.scene = vsm_scene

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


###################
# Objects
###################


def getChildrenHierarchy(parentObject):
    """Return a list with all the children - recursive - of the specified object"""

    allChildren = list()

    def _getChildrenHierarchyRec(parentObject):
        for child in parentObject.children:
            allChildren.append(child)
            _getChildrenHierarchyRec(child)

    _getChildrenHierarchyRec(parentObject)

    return allChildren


def duplicateObject(sourceObject, newName=None, duplicateHierarchy=False):
    """Duplicate (deepcopy) an object and place it in the same collection
    Can be any 3D object, camera...
    """

    def _duplicateObjectRec(sourceObject, sourceParent, dupHierarchy):

        newObject = sourceObject.copy()

        if sourceObject.animation_data is not None and sourceObject.animation_data.action is not None:
            newObject.animation_data.action = sourceObject.animation_data.action.copy()

        # empty objects don't have data
        if sourceObject.data is not None:
            newObject.data = sourceObject.data.copy()
            #  if newObject.data.animation_data is not None:
            if sourceObject.data.animation_data is not None and sourceObject.data.animation_data.action is not None:
                newObject.data.animation_data.action = sourceObject.data.animation_data.action.copy()

        sourceCollections = sourceObject.users_collection
        if len(sourceCollections):
            sourceCollections[0].objects.link(newObject)
        else:
            (sourceObject.users_scene)[0].collection.objects.link(newObject)

        newObject.parent = sourceParent

        if dupHierarchy:
            for child in sourceObject.children:
                _duplicateObjectRec(child, newObject, True)

        return newObject

    rootNewObject = _duplicateObjectRec(sourceObject, None, duplicateHierarchy)
    if newName is not None and "" != newName:
        rootNewObject.name = newName
        rootNewObject.data.name = newName

    return rootNewObject


###################
# Collections
###################


def excludeLayerCollection(scene, collectionName, value: Boolean):
    """Exclude a collection from the view_layer (= check the little Exclude checkbox)"""
    # NOTE: A Layer Collection is different from a Collection and the Exclude parameter is
    # only available on a Layer Collection, which is related to a view_layer
    # Layer Collection: https://docs.blender.org/api/current/bpy.types.LayerCollection.html
    # Collection: https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection

    for viewLayer in scene.view_layers:
        for col in viewLayer.layer_collection.children:
            if col.name == collectionName:
                col.exclude = value
                return


def getCollectionsMatchingNamePattern(scene, pattern):
    """Return the list of the collections of the scene that have the specified pattern in their name.
    Case sensitivity is ignored"""

    colls = list()
    for scnColl in scene.collection.children:
        if -1 != scnColl.name.lower().find(pattern.lower()):
            colls.append(scnColl)
    return colls


###################
# Cameras
###################


def cameras_from_scene(scene):
    """Return the list of all the cameras in the scene"""
    camList = [c for c in scene.objects if c.type == "CAMERA"]
    return camList


def getCameraCurrentlyInViewport(
    context,
    area=None,
):
    """Return the camera currently used by the view, None if
    no camera is used or if the 3D view is not found.
    Requires a valid area VIEW_3D
    """
    area3D = area
    #   print(f"Cam in area3D 01: {area3D}")
    if area is None:
        for screen_area in context.screen.areas:
            if screen_area.type == "VIEW_3D":
                area3D = screen_area
                break

    #    print(f"Cam in area3D 02: {area3D}")

    if area3D is not None:
        for space_data in area3D.spaces:
            if space_data.type == "VIEW_3D":
                #    print(f"Cam in area3D 03: {area3D}")
                if space_data.region_3d.view_perspective == "CAMERA":
                    #        print(f"Cam in area3D 04: {area3D}")
                    if not space_data.use_local_camera:
                        return context.scene.camera

    return None


def makeCameraMatchViewport(context, cam, matchLens=False, putCamInViewport=True):
    """Move, orient and change the lens of the specified camera to match the current viewport framing.
    If the viewport already contains a camera then the settings of this camera will be copied to the specifed one.
    If the viewport is not a 3D view nothing happends.
    Args:
        matchLens: if True then the camera lens will match the viewport camera lens
        putCamInViewport: if True then the camera is also set as the current one in the scene and used
        in the Viewport.
    """
    # Refs: https://blender.stackexchange.com/questions/46391/how-to-convert-spaceview3d-lens-to-field-of-view
    # There is also an operator to do part of the code below: bpy.ops.view3d.camera_to_view()

    scene = context.scene
    props = config.getAddonProps(context.scene)
    #  print(f" makeCameraMatchViewport")

    areaView = getViewportAreaView(context, viewport_index=props.getTargetViewportIndex(context, only_valid=True))
    if areaView is None:
        return

    camInViewport = getCameraCurrentlyInViewport(context, area=areaView)
    camOk = False

    if camInViewport is None:
        # we get the viewport cam settings
        import math

        areaViewRegion = areaView.spaces[0].region_3d

        areaViewRegion.view_camera_zoom = 0.0
        cam.matrix_world = areaViewRegion.view_matrix.inverted()
        if matchLens:
            vmat_inv = areaViewRegion.view_matrix.inverted()
            pmat = areaViewRegion.perspective_matrix @ vmat_inv
            fov = 2.0 * abs(1.0 * math.atan(1.0 / pmat[1][1]))
            #    print(f"Cam fov: {fov}  {fov * 180.0 / math.pi}, zoom: {areaViewRegion.view_camera_zoom}")
            # cam.data.sensor_width = 72
            #    cam.data.lens_unit = "FOV"
            # cam.data.angle = fov - areaViewRegion.view_camera_zoom * math.pi / 180
            cam.data.angle = fov
            # cam.data.lens -= areaViewRegion.view_camera_zoom
            #  areaViewRegion.view_camera_zoom = 0.0
        camOk = True
    else:
        if cam != camInViewport:
            cam.location = camInViewport.location
            cam.rotation_euler = camInViewport.rotation_euler
            if matchLens:
                cam.data.lens = camInViewport.data.lens
            camOk = True

    if putCamInViewport and camOk:
        # align camera to view
        scene.camera = cam
        setCurrentCameraToViewport2(context, area=areaView)


def setCurrentCameraToViewport2(context, area=None):
    """Requires a valid area VIEW_3D"""
    #   print(f"Cam in area3D 01: {area3D}")
    if area is None:
        for screen_area in context.screen.areas:
            if screen_area.type == "VIEW_3D":
                area = screen_area
                break

    #    print(f"Cam in area3D 02: {area3D}")

    if area is not None:
        for space_data in area.spaces:
            if space_data.type == "VIEW_3D":
                space_data.use_local_camera = False
                space_data.region_3d.view_perspective = "CAMERA"
                break


def setCurrentCameraToViewport(context, area=None):

    # print(f"setCurrentCameraToViewport: Num Windows: {len(bpy.context.window_manager.windows)}, area: {area}")

    # area = bpy.context.window_manager.windows[-1].screen.areas[0]
    #         area.type = "IMAGE_EDITOR"
    targetArea = None
    if area is not None:
        rightWin = None
        if area.type != "VIEW_3D":
            for win in bpy.context.window_manager.windows:
                for winArea in win.screen.areas:
                    if winArea == area:
                        rightWin = win
                        break
                if rightWin is not None:
                    break

            if rightWin is not None:
                for winArea in rightWin.screen.areas:
                    #   print(f"Area Type in right win: {winArea.type}")
                    if winArea.type == "VIEW_3D":
                        targetArea = winArea
                    break

    if targetArea is None:
        for win in bpy.context.window_manager.windows:
            for winArea in win.screen.areas:
                #      print(f"Area Type: {winArea.type}")
                if winArea.type == "VIEW_3D":
                    targetArea = winArea
                    break
            if targetArea is not None:
                break

        # for area in context.screen.areas:
        #     print(f"Area Type: {area.type}")
        #     # if area.type == "VIEW_3D"

        # area = next(area for area in context.screen.areas if area.type == "VIEW_3D")

    if targetArea is not None:
        targetArea.spaces[0].use_local_camera = False
        targetArea.spaces[0].region_3d.view_perspective = "CAMERA"

    return


def create_new_camera(camera_name, location=[0, 0, 0], locate_on_cursor=False, camData=None):
    """A unique name will be automatically given to the new camera
    Args:
        camData:    if provided, this camera data is used (without copy) for the new camera,
                    then providing a way to have presets on the camera
    """
    if camData:
        cam_data = camData
        cam_data.name = camera_name
    else:
        cam_data = bpy.data.cameras.new(camera_name)
    cam = bpy.data.objects.new(cam_data.name, cam_data)
    cam.name = cam_data.name

    # add to main collection
    # bpy.context.collection.objects.link(cam)

    # add to a collection named "Cameras"
    camCollName = "Cameras"
    camColl = None
    if camCollName not in bpy.context.scene.collection.children:
        camColl = bpy.data.collections.new(name=camCollName)
        bpy.context.scene.collection.children.link(camColl)
    else:
        camColl = bpy.context.scene.collection.children[camCollName]
    camColl.objects.link(cam)

    if not camData:
        bpy.data.cameras[cam_data.name].lens = 40
        cam_data.lens = 40
        cam_data.clip_start = 0.01

    cam.color[0] = uniform(0, 1)
    cam.color[1] = uniform(0, 1)
    cam.color[2] = uniform(0, 1)

    cam.location = location
    if locate_on_cursor:
        cam.location = bpy.context.scene.cursor.location

    from math import radians

    # align along the Y axis, as in Front view
    # cam_ob.rotation_euler = (radians(90), 0.0, radians(90))
    cam.rotation_euler = (radians(90), 0.0, 0.0)

    # import math
    # import mathutils

    # eul = mathutils.Euler((math.radians(90.0), 0.0, 0.0), "XYZ")

    return cam


def getMovieClipByPath(filepath):
    """Get the first clip with the specified full file name"""
    # TODO: add Case sensitive
    for clip in bpy.data.movieclips:
        if Path(clip.filepath) == filepath:
            return clip
    return None

    # print(f"   -- name:{name}, path: {filepath}")
    # for clip in bpy.data.movieclips:
    #     print(f"   -- clip name:{clip.name}, path: {clip.filepath}")
    #     if clip.name == name:
    #         if filepath is None or clip.filepath == filepath:
    #             return clip
    # return None


def add_background_video_to_cam(
    camera: bpy.types.Camera, movie_path, frame_start, alpha=-1, proxyRenderSize="PROXY_50", relative_path=False
):
    """Camera argument: use camera.data, not the camera object
    proxyRenderSize is PROXY_25, PROXY_50, PROXY_75, PROXY_100, FULL
    Return: the video clip or None if an error occured to read the media or create the clip
    """
    movie_path = Path(movie_path)
    print("add_background_video_to_cam")
    print(f"   movie_path.parent: {movie_path.parent}")
    print(f"   movie_path.name  : {movie_path.name}")

    clipIsValid = False
    if movie_path.is_file():
        try:
            clipIsValid = "FINISHED" in bpy.ops.clip.open(
                directory=str(movie_path.parent), files=[{"name": movie_path.name}], relative_path=relative_path
            )
        except Exception as e:
            # _logger.error("** bpy.context.space_data.lock_camera had an error **")
            color = "\033[91m"
            print(f"{color}\n*** Media cannot be imported: {movie_path} ***{color}")
            print(f"{color}   {e}{color}")
    else:
        color = "\033[91m"
        print(f"{color}\n*** Media not found: {movie_path} ***{color}")

    if clipIsValid:
        # print("   Finished block")
        # clip = bpy.data.movieclips[movie_path.name]
        clip = getMovieClipByPath(movie_path)

        # required since Blender 3.0 (or earlier?) for the frame_start to be taken into account in the viewport
        clip.use_proxy_custom_directory = True

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

    print(f"Clip is valid: {clipIsValid}")
    return clip if clipIsValid else None


def remove_background_video_from_cam(camera: bpy.types.Camera):
    """Camera argument: use camera.data, not the camera object"""
    if camera is not None:
        camera.background_images.clear()
        # remove(image)
        camera.show_background_images = False


###################
# Scene content
###################


def clear_selection():
    selectedObjs = [obj for obj in bpy.context.selected_objects]
    for obj in selectedObjs:
        obj.select_set(False)
    if bpy.context.active_object is not None:
        if "OBJECT" == bpy.context.active_object.mode:
            bpy.context.view_layer.objects.active = None


def select_object(obj: bpy.types.Object, clear_sel=True):
    if clear_sel:
        clear_selection()
    obj.select_set(True)
    if bpy.context.active_object is None:
        bpy.context.view_layer.objects.active = obj

    # if context.active_object is not None and context.active_object.mode != "OBJECT":
    #     bpy.ops.object.mode_set(mode="OBJECT")
    # bpy.ops.object.select_all(action="DESELECT")
    # bpy.context.view_layer.objects.active = gp_child
    # gp_child.select_set(True)
    # gp_child.hide_select = False
    # gp_child.hide_viewport = False
    # gp_child.hide_render = False
    # gp_child.hide_set(False)  # the eye icon


def add_to_selection(obj: bpy.types.Object):
    # bpy.data.objects[obj.name].select_set(True)
    obj.select_set(True)
    # to set the active object
    if bpy.context.active_object is None or "OBJECT" == bpy.context.active_object.mode:
        bpy.context.view_layer.objects.active = obj


###################
# Animation
###################


def getFCurveForSpecifiedTranformAxis(obj: bpy.types.Object, curveType, axis):
    """Return the fCurve of the specified transformation axis, None if not found
    Args:
        obj:    the animated object
        curveType: can be "location", "rotation", "scale"
        axis:   can be "X", "Y", "Z", "W"
    """
    if obj.animation_data is not None:
        action = obj.animation_data.action
        if action is not None:
            for fcurve in action.fcurves:
                if "Object Transforms" == fcurve.group.name and -1 != fcurve.data_path.find(curveType):
                    # rotation data_path can be rotation_quaternion, rotation_euler...
                    if axis.lower() == "x" and 0 == fcurve.array_index:
                        return fcurve
                    elif axis.lower() == "y" and 1 == fcurve.array_index:
                        return fcurve
                    elif axis.lower() == "z" and 2 == fcurve.array_index:
                        return fcurve
                    elif axis.lower() == "w" and 3 == fcurve.array_index:
                        return fcurve
    return None


def getAnimatedTrandformFCurves(obj: bpy.types.Object):
    """Return a list with the animated transformation fCurves of the object"""
    fcurves = list()
    if obj.animation_data is not None:
        action = obj.animation_data.action
        if action is not None:
            for fcurve in action.fcurves:
                if "Object Transform" == fcurve.group.name:
                    fcurves.append(fcurve)
    return fcurves


def clearTransformAnimation(obj: bpy.types.Object, clearPos=True, clearRot=True, clearScale=True, clearLocked=True):
    def _clearCurve(action, type, axis):
        fc = getFCurveForSpecifiedTranformAxis(obj, type, axis)
        if fc and (not fc.lock or clearLocked):
            action.fcurves.remove(fc)

    if obj.animation_data:
        action = obj.animation_data.action
        if action:
            if clearPos:
                _clearCurve(action, "location", "X")
                _clearCurve(action, "location", "Y")
                _clearCurve(action, "location", "Z")
            if clearRot:
                _clearCurve(action, "rotation", "X")
                _clearCurve(action, "rotation", "Y")
                _clearCurve(action, "rotation", "Z")
                _clearCurve(action, "rotation", "W")
            if clearScale:
                _clearCurve(action, "scale", "X")
                _clearCurve(action, "scale", "Y")
                _clearCurve(action, "scale", "Z")

    #     bpy.ops.anim.keyframe_clear_button
    # bpy.ops.object.location_clear()
    # bpy.ops.object.rotation_clear()
    # bpy.ops.object.scale_clear()


def lockTransforms(obj, *, lock=True):
    obj.lock_location[0] = lock
    obj.lock_location[1] = lock
    obj.lock_location[2] = lock
    obj.lock_rotation[0] = lock
    obj.lock_rotation[1] = lock
    obj.lock_rotation[2] = lock
    obj.lock_scale[0] = lock
    obj.lock_scale[1] = lock
    obj.lock_scale[2] = lock


###################
# Color
###################


def slightlyRandomizeColor(refColor, weight=0.8):
    """
    refColor is supposed to be linear, returned color is linear too
    Args:
        refColor: the input color. Can be RGB or RGBA. Alpha is not modified.
        weight: value in [0, 1]. The closer weight is to 1, the less the color is changed
    """
    from random import uniform

    newColor = [uniform(0, 1), uniform(0, 1), uniform(0, 1)]
    for i in range(0, 3):
        newColor[i] = refColor[i] * weight + newColor[i] * (1.0 - weight)

    if len(refColor) == 4:
        newColor.append(refColor[3])

    return newColor


def color_is_dark(color, threshold):
    """
    Args:
        color: tupple 4
        treshold: value between 0.0 and 1.0
    """
    from statistics import mean

    return mean(color[:-1]) < threshold


def darken_color(color):
    factor = 0.6
    d_color = (color[0] * factor, color[1] * factor, color[2] * factor, color[3] * 1.0)
    return d_color


def lighten_color(color, value=0.1):
    """Do a ADD"""
    d_color = (min(color[0] + value, 1.0), min(color[1] + value, 1.0), min(color[2] + value, 1.0), color[3])
    return d_color


def value_to_linear(value):
    invGamma = 1.0 / 0.45
    return pow(value, invGamma)


def color_to_linear(color, convertAlpha=False):
    """Convert a sRGB color to a linear color
    Args:
        color:  array of 4 floats belonging to range [0, 1]"""
    # 0.45 = 1/2.2
    invGamma = 1.0 / 0.45
    alpha = pow(color[3], invGamma) if convertAlpha else color[3]
    convertedColor = (pow(color[0], invGamma), pow(color[1], invGamma), pow(color[2], invGamma), alpha)
    return convertedColor


def value_to_sRGB(value):
    gamma = 0.45
    return pow(value, gamma)


def color_to_sRGB(color, convertAlpha=False):
    """Convert a linear color to a sRGB color
    Args:
        color:  array of 4 floats belonging to range [0, 1]"""
    # 0.45 = 1/2.2
    gamma = 0.45
    alpha = pow(color[3], gamma) if convertAlpha else color[3]
    convertedColor = (pow(color[0], gamma), pow(color[1], gamma), pow(color[2], gamma), alpha)
    return convertedColor


def set_color_alpha(color, alpha):
    return (color[0], color[1], color[2], alpha)


def alpha_to_linear(alpha):
    # alpha is already treated as being sRGB... We make it more "linear"
    return pow(alpha, 1.0 / 0.65)


###################
# Images
###################


def getDataImageFromPath(filepath, filename):
    """Return the image with the specified file name from data, load it if not found
    Args:
        filepath: eg: "c:\\temp\\"
        filename: eg: WALL_1773.png
    """
    img = None
    if filename in bpy.data.images:
        img = bpy.data.images[filename]
    # if img:
    # if img.filepath == filepath:

    if not img:
        # TODO: test filepath existence and last char
        img = bpy.data.images.load(os.path.join(filepath, filename))

    return img


###################
# Dev
###################


def segment_is_in_range(segment_start, segment_end, range_start, range_end, partly_inside=True):
    if partly_inside:
        if segment_start < range_start:
            return segment_end >= range_start
        else:
            return segment_start <= range_end  # < ?
    else:
        return segment_start >= range_start and segment_end <= range_end


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def remap(value, old_min, old_max, new_min, new_max):
    value = clamp(value, old_min, old_max)
    old_range = old_max - old_min
    if old_range == 0:
        new_value = new_min
    else:
        new_range = new_max - new_min
        new_value = (((value - old_min) * new_range) / old_range) + new_min

    return new_value
