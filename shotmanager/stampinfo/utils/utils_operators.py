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
Utils operators
"""

import json

# from tokenize import String

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from . import utils


class UAS_SIUtils_OpenAddonFolder(Operator):
    bl_idname = "uas_si_utils.open_addon_folder"
    bl_label = "Open Add-on Folder"
    bl_description = (
        "Open the folder in which this add-on is installed," "\nand print the user script folder paths in the Terminal"
    )

    def execute(self, context):
        # https://blender.stackexchange.com/questions/64129/get-blender-scripts-path
        # x = bpy.utils.script_path_user()
        # bpy.utils.script_paths() returns the list of script folders

        addonPath = utils.addonPath()
        print(f"\nAdd-on Installation Path:\n  - {addonPath}\\")
        scriptPaths = bpy.utils.script_paths()
        print("Script paths:")
        for p in scriptPaths:
            print(f"   - {p}\\")
        print("\n")

        bpy.ops.uas_shot_manager.open_explorer("INVOKE_DEFAULT", path=addonPath)

        return {"FINISHED"}


_classes = (UAS_SIUtils_OpenAddonFolder,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
