import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


def addonVersion(addonName):
    import addon_utils

    versionStr = "-"
    versionTupple = [
        addon.bl_info.get("version", (-1, -1, -1))
        for addon in addon_utils.modules()
        if addon.bl_info["name"] == addonName
    ]
    if len(versionTupple):
        versionTupple = versionTupple[0]
        versionStr = str(versionTupple[0]) + "." + str(versionTupple[1]) + "." + str(versionTupple[2])

    return versionStr


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


def cameras_from_scene(scene):
    """ Return the list of all the cameras in the scene
    """
    camList = [c for c in scene.objects if c.type == "CAMERA"]
    return camList


def duplicateObject(sourceObject):
    """ Duplicate (deepcopy) an object and place it in the same collection
    """
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


_classes = (UAS_ShotManager_OpenExplorer,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
