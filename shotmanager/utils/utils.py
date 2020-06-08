

import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


class PropertyRestoreCtx:
    """
    Restore property values at the end of the block.

    """
    def __init__ (self, *properties):
        self.backups = None
        self.props = properties

    def __enter__ ( self ):
        self.backups = list ()
        for p in self.props:
            try:
                self.backups.append ( ( p[ 0 ], p[ 1 ], getattr ( p[ 0 ], p[ 1 ] ) ) )
            except AttributeError:
                continue

    def __exit__ ( self, exc_type, exc_val, exc_tb ):
        for p in self.backups:
            setattr ( p[ 0 ], p[ 1 ], p[ 2 ] )


class UAS_ShotManager_OpenExplorer(Operator):
    bl_idname = "uas_shot_manager.render_openexplorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory"

    path: StringProperty()

    def execute(self, context):
        pathToOpen = self.path
        absPathToOpen = bpy.path.abspath(pathToOpen)
        head, tail = os.path.split(absPathToOpen)
        #wkip pouvoir ouvrir path relatif
        absPathToOpen = head + "\\"

        if Path(absPathToOpen).exists():
            subprocess.Popen(f"explorer \"{absPathToOpen}\"")
        else:
            print("Open Explorer failed: Path not found: \"" + absPathToOpen + "\"")

        return {"FINISHED"}


def ShowMessageBox(message="", title="Message Box", icon="INFO"):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# #Shows a message box with a specific message 
# ShowMessageBox("This is a message") 

# #Shows a message box with a message and custom title
# ShowMessageBox("This is a message", "This is a custom title")

# #Shows a message box with a message, custom title, and a specific icon
# ShowMessageBox("This is a message", "This is a custom title", 'ERROR')

def file_path_from_uri ( uri ):
    path = unquote_plus ( urlparse ( uri ).path ).replace ( "\\", "//" )
    if re.match ( r"^/\S:.*", path ):  # Remove leading /
        path = path[ 1: ]

    return path


def add_background_video_to_cam ( camera: bpy.types.Camera, movie_path, frame_start = 1 ):
    movie_path = Path ( movie_path )
    if not movie_path.exists ( ):
        return

    if "FINISHED" in bpy.ops.clip.open ( directory = str ( movie_path.parent ), files = [ { "name": movie_path.name } ] ):
        clip = bpy.data.movieclips[ movie_path.name ]
        clip.frame_start = frame_start
        camera.show_background_images = True
        bg = camera.background_images.new( )
        bg.source = "MOVIE_CLIP"
        bg.clip = clip

_classes = (UAS_ShotManager_OpenExplorer, )

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
