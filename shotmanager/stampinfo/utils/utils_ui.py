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
UI utilities
"""


import os
import subprocess

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper

from shotmanager.utils.utils_os import open_folder
from shotmanager.utils.utils import convertVersionIntToStr


###################
# UI
###################


def collapsable_panel(
    layout: bpy.types.UILayout,
    data: bpy.types.AnyType,
    property: str,
    alert: bool = False,
    text=None,
):
    """Draw an arrow to collapse or extend a panel.
    Return the title row
    Args:
        layout: parent component
        data: the object with the properties
        property: the boolean used to store the rolled-down state of the panel
        alert: is the title bar of the panel is drawn in alert mode
        text: the title of the panel
    eg: collapsable_panel(layout, addon_props, "display_users", text="Server Users")
        if addon_props.addonPrefs_ui_expanded: ...
    """
    row = layout.row(align=True)
    row.alignment = "LEFT"
    # row.scale_x = 0.9
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


####################################################################


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
# in stampinfo code to a call to uas_sm_stamp_info.querybox
def reset_all_properties():
    from shotmanager import stampinfo

    print("reset_all_properties")
    stampinfo.stampInfo_resetProperties()


class UAS_SMStampInfo_OT_Querybox(Operator):
    """Display a query dialog box

    A message can be drawn on several lines when containing the separator \n
    """

    bl_idname = "uas_sm_stamp_info.querybox"
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


_classes = (UAS_SMStampInfo_OT_Querybox,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
