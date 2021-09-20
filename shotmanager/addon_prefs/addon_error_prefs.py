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
add-on global preferences
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty

from ..ui.sm_dependencies_ui import drawDependencies

from ..config import config


class UAS_ShotManager_AddonErrorPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["shotmanager"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    ########################################################################
    # general ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    # ****** hidden settings:
    # ------------------------------

    install_failed: BoolProperty(
        name="Install failed", default=True,
    )

    ##################################################################################
    # Draw
    ##################################################################################
    def draw(self, context):
        layout = self.layout
        # prefs = context.preferences.addons["shotmanager"].preferences

        box = layout.box()
        box.alert = True
        titleRow = box.row()
        titleRow.alignment = "CENTER"
        titleRow.label(text="   ••• Ubisoft Shot Manager installation failed •••", icon="ERROR")
        titleRow.label(text="", icon="ERROR")

        box.separator(factor=0.3)
        row = box.row()
        split = row.split(factor=0.3)
        rowLeft = split.row()
        rowLeft.separator(factor=3)
        rowLeft.label(text="Returned Error(s):")

        # row = box.row()
        # row.separator(factor=4)
        col = split.column()
        for message in config.installation_errors:
            col.label(text=f"- {message}")
        # row.separator()

        box.separator(factor=0.3)
        row = box.row()
        row.separator(factor=3)
        row.label(text="Mone information in the Blender System Console")

        # box.separator(factor=0.3)
        tipsRow = box.row()
        tipsRow.separator(factor=2)
        tipsBox = tipsRow.box()
        tipsBox.label(text="To fix the issue: remove the add-on, check the points below and restart the install.")
        # tipsBox.separator(factor=4)
        col = tipsBox.column()
        col.label(text="      • Launch Blender in Admin mode")
        col.label(text="      • Be sure your computer is connected to internet")
        col.label(text="      • Be sure a firewall is not blocking information (or use OpenVPN or equivalent)")
        tipsRow.separator(factor=2)
        box.separator(factor=0.3)

        row = box.row(align=True)
        row.label(text="If the issus persists check the Installation Troubles FAQ:")
        rowRight = row.row()
        rowRight.alignment = "RIGHT"
        rowRight.scale_x = 1.0
        doc_op = rowRight.operator("shotmanager.open_documentation_url", text="Shot Manager FAQ")
        doc_op.path = "https://ubisoft-shotmanager.readthedocs.io/en/latest/troubleshoot/faq.html#installation"
        doc_op.tooltip = "Open online FAQ: " + doc_op.path
        box.separator(factor=0.3)

        drawDependencies(context, layout)


_classes = (UAS_ShotManager_AddonErrorPrefs,)


def register():
    print("       - Registering Add-on Installation Error Preferences")
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    print("       - Unregistering Add-on Installation Error Preferences")
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
