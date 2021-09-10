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

# from ..config import config


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

        layout.label(text="Install failed")
        layout.label(text="See Installation Troubles FAQ in the online documentation:")

        row = layout.row(align=True)
        row.operator(
            "shotmanager.open_documentation_url", text="Documentation"
        ).path = "https://ubisoft-shotmanager.readthedocs.io/en/latest/troubleshoot/faq.html#installation"


_classes = (UAS_ShotManager_AddonErrorPrefs,)


def register():
    print("       - Registering Add-on Installation Error Preferences")
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    print("       - Unregistering Add-on Installation Error Preferences")
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
