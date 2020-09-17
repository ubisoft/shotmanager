import os
import re
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

import bpy


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


def display_addon_registered_version(addon_name):
    versionTupple = addonVersion(addon_name)
    if versionTupple is not None:
        print(
            "\n*** *** Registering "
            + addon_name
            + " Add-on - version: "
            + versionTupple[0]
            + "  ("
            + str(versionTupple[1])
            + ") *** ***"
        )
    else:
        print('\n *** Cannot find registered version for add-on "' + addon_name + '" ***\n')
    return versionTupple


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


def file_path_from_url(uri):
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


def getSceneVSE(vsm_sceneName, createVseTab=True):
    """ Return the scene that has the name held by vsm_sceneName and adds a VSE in it if there is not already one.
        Use <returned scene>.sequence_editor to get the vse of the scene
    """
    # vsm_sceneName = "VideoShotManger"
    vsm_scene = None

    if vsm_sceneName in bpy.data.scenes:
        vsm_scene = bpy.data.scenes[vsm_sceneName]
    else:
        vsm_scene = bpy.data.scenes.new(name=vsm_sceneName)
        vsm_scene.render.fps = bpy.context.scene.render.fps

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


def duplicateObject(sourceObject):
    """ Duplicate (deepcopy) an object and place it in the same collection
    """
    newObject = sourceObject.copy()
    if newObject.animation_data is not None:
        newObject.animation_data.action = sourceObject.animation_data.action.copy()

    newObject.data = sourceObject.data.copy()
    if newObject.data.animation_data is not None:
        newObject.data.animation_data.action = sourceObject.data.animation_data.action.copy()

    sourceCollections = sourceObject.users_collection
    if len(sourceCollections):
        sourceCollections[0].objects.link(newObject)
    else:
        (sourceObject.users_scene)[0].collection.objects.link(newObject)
    return newObject


###################
# Cameras
###################


def cameras_from_scene(scene):
    """ Return the list of all the cameras in the scene
    """
    camList = [c for c in scene.objects if c.type == "CAMERA"]
    return camList


def setCurrentCameraToViewport():
    area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")

    area.spaces[0].use_local_camera = False
    area.spaces[0].region_3d.view_perspective = "CAMERA"

    return


def create_new_camera(camera_name, location=[0, 0, 0], locate_on_cursor=False):
    cam = bpy.data.cameras.new(camera_name)
    cam_ob = bpy.data.objects.new(cam.name, cam)
    cam_ob.name = cam.name
    bpy.context.collection.objects.link(cam_ob)

    bpy.data.cameras[cam.name].lens = 40

    cam_ob.location = location
    if locate_on_cursor:
        cam_ob.location = bpy.context.scene.cursor.location

    from math import radians

    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

    # import math
    # import mathutils

    # eul = mathutils.Euler((math.radians(90.0), 0.0, 0.0), "XYZ")

    # if cam_ob.rotation_mode == "QUATERNION":
    #     cam_ob.rotation_quaternion = eul.to_quaternion()
    # elif cam_ob.rotation_mode == "AXIS_ANGLE":
    #     q = eul.to_quaternion()
    #     cam_ob.rotation_axis_angle[0] = q.angle
    #     cam_ob.rotation_axis_angle[1:] = q.axis
    # else:
    #     cam_ob.rotation_euler = (
    #         eul if eul.order == cam_ob.rotation_mode else (eul.to_quaternion().to_euler(cam_ob.rotation_mode))
    #     )

    return cam_ob


###################
# Scene content
###################


def clear_selection():
    if bpy.context.active_object is not None:
        bpy.context.active_object.select_set(False)
    for obj in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = obj


def add_to_selection(obj):
    # bpy.data.objects[obj.name].select_set(True)
    # bpy.context.view_layer.objects.active = bpy.data.objects['Sphere']
    obj.select_set(True)
    # to set the active object
    bpy.context.view_layer.objects.active = obj


###################
# Color
###################


def slightlyRandomizeColor(refColor, weight=0.8):
    """
        refColor is supposed to be linear, returned color is linear too
        refColor can be RGB or RGBA. Alpha is not modified.
    """
    from random import uniform

    newColor = [uniform(0, 1), uniform(0, 1), uniform(0, 1)]
    for i in range(0, 3):
        newColor[i] = refColor[i] * weight + newColor[i] * (1.0 - weight)

    if len(refColor) == 4:
        newColor.append(refColor[3])

    return newColor


def darken_color(color):
    factor = 0.6
    d_color = (color[0] * factor, color[1] * factor, color[2] * factor, color[3] * 1.0)
    return d_color


def linearizeColor(color):
    gamma = 0.45
    d_color = (pow(color[0], gamma), pow(color[1], gamma), pow(color[2], gamma), color[3] * 1.0)
    return d_color


def sRGBColor(color):
    gamma = 1.0 / 0.45
    d_color = (pow(color[0], gamma), pow(color[1], gamma), pow(color[2], gamma), color[3] * 1.0)
    return d_color


###################
# Various
###################


def segment_is_in_range(segment_start, segment_end, range_start, range_end, partly_inside=True):
    if partly_inside:
        if segment_start < range_start:
            return segment_end >= range_start
        else:
            return segment_start <= range_end  # < ?
    else:
        return segment_start >= range_start and segment_end <= range_end
