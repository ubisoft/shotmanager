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

import sys

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, StringProperty

from ..ui.dependencies_ui import drawDependencies

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_AddonErrorPrefs(AddonPreferences):
    """
    Use this to get these prefs:
    prefs = config.getAddonPrefs()
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
        name="Install Failed",
        default=True,
    )
    error_message: StringProperty(
        name="Error Message",
        default="",
    )
    verbose: BoolProperty(
        name="Verbose",
        default=False,
    )

    ##################################################################################
    # Draw
    ##################################################################################
    def draw(self, context):
        layout = self.layout
        prefs_addon = config.getAddonPrefs()

        box = layout.box()
        box.alert = True
        mainCol = box.column()
        mainCol.scale_y = 1.2
        titleRow = mainCol.row()
        titleRow.alignment = "CENTER"
        titleRow.label(text="   ••• Ubisoft Shot Manager installation failed •••", icon="ERROR")
        titleRow.label(text="", icon="ERROR")

        row = mainCol.row()
        split = row.split(factor=0.25)
        rowLeft = split.row()
        rowLeft.separator(factor=1.9)
        rowLeft.label(text="Returned Error(s):")

        col = split.column()
        # for message in config.installation_errors:
        #     col.label(text=f"- {message[0]}")
        col.label(text=f"- {prefs_addon.error_message}")

        row = mainCol.row()
        row.separator(factor=2)
        row.label(text="More information in the Blender System Console")
        if sys.platform == "win32":
            rowRight = row.row()
            rowRight.alignment = "RIGHT"
            rowRight.scale_y = 0.9
            rowRight.operator("wm.console_toggle", text="Console")
            rowRight.separator(factor=2)

        tipsRow = mainCol.row()
        tipsRow.separator(factor=1.5)
        tipsBox = tipsRow.box()
        col = tipsBox.column()
        col.label(text="To fix the issue:")
        col.separator(factor=0.7)
        col.scale_y = 0.6
        col.label(text="      • Remove the add-on")
        col.label(text="      • Close Blender")
        col.label(text="      • Be sure your computer is connected to the internet")
        col.label(text="      • Be sure no firewall is blocking the connection (or use OpenVPN or equivalent)")
        col.label(text="      • Launch Blender in Admin mode")
        col.label(text="      • Restart the install")
        tipsRow.separator(factor=2)

        box.separator(factor=0.1)
        row = box.row(align=True)
        row.label(text="If the issue persists check the Installation Troubles FAQ:")
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
    _logger.debug_ext("       - Registering Add-on Installation Error Preferences", form="REG")

    for cls in _classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            _logger.warning_ext("SM: Trying to register again 'addon_error_prefs'")


def unregister():
    _logger.debug_ext("       - Unregistering Add-on Installation Error Preferences", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
