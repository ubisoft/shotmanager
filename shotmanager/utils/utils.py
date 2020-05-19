

#-*- coding: utf-8 -*-
#
import os
from pathlib import Path
import subprocess
import importlib

import bpy
from bpy.types import Operator
from bpy.props import StringProperty



class PropertyRestoreCtx:
    """
    Restore property values at the end of the block.

    """
    def __init__ ( self, *properties ):
        self.backups = None
        self.props = properties

    def __enter__ ( self ):
        self.backups = list ( )
        for p in self.props:
            try:
                self.backups.append ( ( p[ 0 ], p[ 1 ], getattr ( p[ 0 ], p[ 1 ] ) ) )
            except AttributeError:
                continue

    def __exit__ ( self, exc_type, exc_val, exc_tb ):
        for p in self.backups:
            setattr ( p[ 0 ], p[ 1 ], p[ 2 ] )



# wkip use icon FILEBROWSER
class UAS_ShotManager_OpenExplorer( Operator ):
    bl_idname   = "uas_shot_manager.render_openexplorer"
    bl_label    = "Open Explorer"
    bl_description  = "Open an Explorer window located at the render output directory"

    path: StringProperty ( )

    def execute ( self, context ):
        pathToOpen = self.path
        absPathToOpen = bpy.path.abspath(pathToOpen)
        head, tail = os.path.split(absPathToOpen)
        #wkip pouvoir ouvrir path relatif
        absPathToOpen = head + "\\"

        if Path ( absPathToOpen ).exists():
            subprocess.Popen ( f"explorer \"{absPathToOpen}\"" )
        else:
            print("Open Explorer failed: Path not found: \"" + absPathToOpen + "\"")

        return { "FINISHED" }



def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text = message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


# #Shows a message box with a specific message 
# ShowMessageBox("This is a message") 

# #Shows a message box with a message and custom title
# ShowMessageBox("This is a message", "This is a custom title")

# #Shows a message box with a message, custom title, and a specific icon
# ShowMessageBox("This is a message", "This is a custom title", 'ERROR')


_classes = ( 
            UAS_ShotManager_OpenExplorer,
             )


def register ( ):
    for cls in _classes:
        bpy.utils.register_class ( cls )


def unregister ( ):
    for cls in reversed ( _classes ):
        bpy.utils.unregister_class ( cls )
