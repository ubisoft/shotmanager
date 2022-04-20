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
    materialName: StringProperty(default="")


class UAS_GreasePencil_FrameTemplate(PropertyGroup):
    """Contains the grease pencil related to the shot"""

    usagePresets: CollectionProperty(type=UAS_ShotManager_FrameUsagePreset)

    def initialize(self, mode="SCENE"):
        """
        Args:
            mode:   can be SCENE or ADDON_PREFS"
        """
        # self.parent = parent

        _logger.debug_ext(f"Initializing storyboard template preset list for {mode}", col="GREEN")
        self.updatePresets(mode=mode)
        print("herehere 02")

    def updatePresets(self, mode="SCENE"):
        """
        Args:
            mode:   can be SCENE or ADDON_PREFS"
        """
        _logger.debug_ext(f"updatePresets() for storyboard template preset list for {mode}", col="GREEN")
        # Can be SCENE or ADDON_PREFS"
        prefs = bpy.context.preferences.addons["shotmanager"].preferences
        if "SCENE" == mode:
            props = bpy.context.scene.UAS_shot_manager_props
        else:
            props = prefs

        print("herehere 01")
        if "ADDON_PREFS" == mode:
            _logger.debug_ext(f"   In ADDON PREFS Add Presets", col="GREEN")
            # initialize the add-on preferences set of presets
            # wkipwkipwkip
            # Canvas
            _use = True
            _layerName = "_Canvas_"
            _matName = "_Canvas_Mat"
            props.stb_frameTemplate.addPreset("CANVAS", _use, _layerName, _matName)

            # BG #############
            _use = True
            _layerName = "BG Fills"
            _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("BG_FILLS", _use, _layerName, _matName)
            _use = True
            _layerName = "BG Lines"
            _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("BG_LINES", _use, _layerName, _matName)

            # MG #############
            _use = True
            _layerName = "MiddleG Fills"
            _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("MG_FILLS", _use, _layerName, _matName)
            _use = True
            _layerName = "MiddleG Lines"
            _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("MG_LINES", _use, _layerName, _matName)

            # FG #############
            _use = True
            _layerName = "FG Fills"
            _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("FG_FILLS", _use, _layerName, _matName)
            _use = True
            _layerName = "FG Lines"
            _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("FG_LINES", _use, _layerName, _matName)

            # Rough #############
            _use = True
            _layerName = "Rough"
            _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("ROUGH", _use, _layerName, _matName)

        else:
            # SCENE
            # initialize the template presets of the scene from the add-on preferences
            _logger.debug_ext(f"   In SCENE Add Presets", col="GREEN")
            # bpy.ops.uas_shot_manager.greasepencil_template_panel(mode=mode)

            prefsTemplate = prefs.stb_frameTemplate

            def _createPreset(id):
                preset = self.getPresetByID(id)
                if preset is None:
                    preset = self.addPreset(id)
                if preset is not None:
                    # prefsTemplate.getPreset(preset, preset.id, preset.used, preset.layerName, preset.materialName)
                    prefsTemplate.getPreset(preset, preset.id, "used", "layerName", "materialName")

            # order is important
            presets = ["ROUGH", "FG_LINES", "FG_FILLS", "MG_LINES", "MG_FILLS", "BG_LINES", "BG_FILLS", "CANVAS"]
            for p in reversed(presets):
                _createPreset(p)

        print("herehere 03")

    def getPresetByID(self, id):
        preset = None
        if len(self.usagePresets):
            for p in self.usagePresets:
                if id == p.id:
                    return p
        return preset

    def addPreset(self, id, used=False, layerName="", materialName="", updateExisting=True):
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
            preset.materialName = materialName

        return preset

    def getPreset(self, prop, id, used, layerName, materialName):
        preset = self.getPresetByID(id)
        if preset is not None:
            setattr(prop, used, preset.used)
            setattr(prop, layerName, preset.layerName)
            setattr(prop, materialName, preset.materialName)


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
