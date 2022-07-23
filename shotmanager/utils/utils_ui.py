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
UI utilities
"""


import os
from pathlib import Path
import subprocess

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper

from .utils_os import open_folder
from .utils import convertVersionIntToStr

from shotmanager.config import config

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

###################
# UI
###################


def redrawAll(context):
    """Redraw all"""
    for area in context.screen.areas:
        area.tag_redraw()
    # context.scene.frame_current = context.scene.frame_current


def drawStampInfoBut(layout):
    """Draw a button to toggle the display of Stamp Info panel in the 3D View tab
    The button is disabled if Stamp Info is not available
    Return True if Stamp Info is available, false otherwise"""
    prefs_stampInfo = None
    if bpy.context.scene.UAS_shot_manager_props.isStampInfoAvailable():
        prefs_stampInfo = bpy.context.preferences.addons["shotmanager"].preferences
    icon = config.icons_col["StampInfo_32"]
    butsubrow = layout.row()
    butsubrow.scale_x = 1.5
    if prefs_stampInfo is not None:
        butsubrow.prop(prefs_stampInfo, "stampInfo_display_main_panel", text="", icon_value=icon.icon_id)
    else:
        butsubrow.operator(
            "uas.empty_operator", text="", icon_value=icon.icon_id
        ).tooltip = "Display Stamp Info panel in the 3D View tabs.\n\n*** Ubisoft Stamp Info add-on is not installed or not activated ***"

    return prefs_stampInfo is not None


def drawSeparatorLine(layout, lower_height=1.0, higher_height=0.0):
    col = layout.column()

    if 0 < higher_height:
        row = col.row()
        row.scale_y = higher_height
        row.separator()

    row = col.row()
    row.scale_y = 0.2
    row.alignment = "CENTER"
    row.label(text="_____________________")

    row = col.row()
    row.scale_y = lower_height
    row.separator()


def collapsable_panel(
    layout: bpy.types.UILayout, data: bpy.types.AnyType, property: str, alert: bool = False, text=None, scale_x=None
):
    """Draw an arrow to collapse or extend a panel.
    Return the title row
    Args:
        layout: parent component
        data: the object with the properties
        property: the boolean used to store the rolled-down state of the panel
        alert: is the title bar of the panel is drawn in alert mode
        text: the title of the panel
        scale_x: Used to reduce the distance on the left side of the arrow. Works better
            with a text left to None or set to ""
    eg: collapsable_panel(layout, addon_props, "display_users", text="Server Users")
        if addon_props.addonPrefs_ui_expanded: ...
    """
    row = layout.row(align=True)
    row.alignment = "LEFT"
    if scale_x is not None:
        row.scale_x = scale_x
    # row.separator(factor=0.5)
    row.alert = alert
    row.prop(
        data,
        property,
        icon="TRIA_DOWN" if getattr(data, property) else "TRIA_RIGHT",
        icon_only=True,
        emboss=False,
        text=text,
    )
    if alert:
        row.label(text="", icon="ERROR")
    # row.label(text=text)
    row.alert = False

    return row


###################
# Open doc and explorers
###################


class UAS_ShotManager_OpenExplorer(Operator):
    bl_idname = "uas_shot_manager.open_explorer"
    bl_label = "Open Explorer"
    bl_description = (
        "Open an Explorer window located at the render output directory." "\n+ Shift: Copy the path into the clipboard"
    )

    path: StringProperty()

    def invoke(self, context, event):
        absPathToOpen = bpy.path.abspath(self.path)
        head, tail = os.path.split(absPathToOpen)
        absPathToOpen = head + "\\"

        if event.shift:

            def _copy_to_clipboard(txt):
                cmd = "echo " + txt.strip() + "|clip"
                return subprocess.check_call(cmd, shell=True)

            _copy_to_clipboard(absPathToOpen)

        else:
            # wkipwkip
            if Path(absPathToOpen).exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen)}"')
            elif Path(absPathToOpen).parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent}"')
            elif Path(absPathToOpen).parent.parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent.parent}"')
            else:
                print(f"Open Explorer failed: Path not found: {Path(absPathToOpen)}")
                from ..utils.utils import ShowMessageBox

                ShowMessageBox(f"{absPathToOpen} not found", "Open Explorer - Directory not found", "ERROR")

        return {"FINISHED"}


class UAS_SM_Open_Documentation_Url(Operator):  # noqa 801
    bl_idname = "shotmanager.open_documentation_url"
    bl_label = ""
    bl_description = "Open web page." "\n+ Shift: Copy the URL into the clipboard"

    tooltip: StringProperty(default="")
    path: StringProperty()

    @classmethod
    def description(self, context, properties):
        descr = properties.tooltip if "" != properties.tooltip else "Open web page."
        descr += "\n+ Shift: Copy the URL into the clipboard"
        return descr

    def invoke(self, context, event):
        if event.shift:
            # copy path to clipboard
            cmd = "echo " + (self.path).strip() + "|clip"
            subprocess.check_call(cmd, shell=True)
        else:
            open_folder(self.path)

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_OpenFileBrowser(Operator, ImportHelper):
    bl_idname = "shotmanager.openfilebrowser"
    bl_label = "Open"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga,*.bmp", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        bpy.context.scene.UAS_SM_StampInfo_Settings.logoFilepath = self.filepath

        return {"FINISHED"}


def show_message_box(message="", title="Message Box", icon="INFO"):
    """Display a message box

    A message can be drawn on several lines when containing the separator \n

    Shows a message box with a specific message:
    -> show_message_box("This is a message")

    Shows a message box with a message and custom title
    -> show_message_box("This is a message", "This is a custom title")

    Shows a message box with a message, custom title, and a specific icon
    -> show_message_box("This is a message", "This is a custom title", 'ERROR')
    """

    messages = message.split("\n")

    def draw(self, context):
        layout = self.layout

        for s in messages:
            layout.label(text=s)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# TODO: Cleaning
# Dev note: This function has to be here for the moment cause it is passed
# in stampinfo code to a call to uas_shotmanager.querybox
def reset_render_properties():
    props = bpy.context.scene.UAS_shot_manager_props
    props.reset_render_properties()


class UAS_ShotManager_OT_Querybox(Operator):
    """Display a query dialog box

    A message can be drawn on several lines when containing the separator \n
    """

    bl_idname = "uas_shotmanager.querybox"
    bl_label = "Please confirm:"
    # bl_description = "..."
    bl_options = {"INTERNAL"}

    width: bpy.props.IntProperty(default=400)
    message: bpy.props.StringProperty(default="Do you confirm the operation?")
    function_name: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.width)

    def draw(self, context):

        messages = self.message.split("\n")

        layout = self.layout
        layout.separator(factor=1)

        for s in messages:
            layout.label(text=s)

        # row = layout.row()
        # row.separator(factor=2)
        # row.label(text=self.message)

        layout.separator()

    def execute(self, context):
        eval(self.function_name + "()")
        # try:
        #     eval(self.function_name + "()")
        # except Exception:
        #     print(f"*** Function {self.function_name} not found ***")

        return {"FINISHED"}


####################################################################


class UAS_ShotManager_UpdateDialog(Operator):
    bl_idname = "uas_shot_manager.update_dialog"
    bl_label = "Add-on Update Available"
    bl_description = "Open a dialog window presenting the available update of the add-on"

    # can be a web url or an intranet path
    url: StringProperty(default="")

    addonName: StringProperty(default="")

    def invoke(self, context, event):
        self.addonName = "Ubisoft Shot Manager"
        self.url = "https://github.com/ubisoft/shotmanager/releases/latest"

        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        prefs = context.preferences.addons["shotmanager"].preferences

        layout = self.layout
        box = layout.box()
        col = box.column()

        sepRow = col.row()
        sepRow.separator(factor=0.5)

        row = col.row()
        newVersionStr = f"V. {convertVersionIntToStr(prefs.newAvailableVersion)}"
        row.label(text=f"A new version of {self.addonName} is available on GitHub: {newVersionStr}")

        sepRow = col.row()
        sepRow.separator(factor=0.5)

        row = col.row()
        row.label(text="You can download it here:")

        doc_op = row.operator("shotmanager.open_documentation_url", text="Download Latest", icon="URL")
        doc_op.path = self.url
        doc_op.tooltip = "Open latest Shot Manager download page: " + doc_op.path

        sepRow = col.row()
        sepRow.separator(factor=0.5)

    def execute(self, context):
        return {"FINISHED"}


####################################################################


_classes = (
    UAS_ShotManager_OpenExplorer,
    UAS_SM_Open_Documentation_Url,
    UAS_ShotManager_OpenFileBrowser,
    UAS_ShotManager_OT_Querybox,
    UAS_ShotManager_UpdateDialog,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            _logger.debug_ext(f"Error in Unregister of {cls}")
            pass
