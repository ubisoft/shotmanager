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
Shot Manager grease pencil operators
"""


import bpy
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, StringProperty, BoolProperty

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_FrameUsagePreset(PropertyGroup):

    id: StringProperty(default="ID")
    used: BoolProperty(default=False)
    layerName: StringProperty(default="")


class UAS_GreasePencil_FrameTemplate(PropertyGroup):
    """Contains the grease pencil related to the shot"""

    usagePresets: CollectionProperty(type=UAS_ShotManager_FrameUsagePreset)

    def initialize(self):
        # self.parent = parent

        self.updatePresets()

    def updatePresets(self):
        bpy.ops.uas_shot_manager.greasepencil_template_panel()

    def getPresetByID(self, id):
        preset = None
        if len(self.usagePresets):
            for p in self.usagePresets:
                if id == p.id:
                    return p
        return preset

    def addPreset(self, id, used=False, layerName="", updateExisting=True):
        """Create a new preset and return it
        If a preset with the same ID already exists then it is returned as is
        Args:
            id: Can be anything (nothing hardcoded in SM) but most common are:
                "CANVAS", "BG_LINES", "BG_FILLS", "MG_LINES", "MG_FILLS", "FG_LINES", "FG_FILLS", "ROUGH"
        """
        preset = self.getPresetByID(id)
        isNewPreset = False

        if preset is None and "" != id:
            preset = self.usagePresets.add()
            isNewPreset = True

        if isNewPreset or updateExisting:
            preset.id = id
            preset.used = used
            preset.layerName = layerName

        return preset


_classes = (
    UAS_ShotManager_FrameUsagePreset,
    UAS_GreasePencil_FrameTemplate,
)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
