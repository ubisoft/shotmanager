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
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    StringProperty,
)

from .greasepencil_frame_usage_preset import UAS_ShotManager_FrameUsagePreset
from shotmanager.features.storyboard.frame_grid.storyboard_frame_grid_props import UAS_ShotManager_FrameGrid
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_GreasepencilObjSettings(PropertyGroup):
    """Store the active layer used by an edited grease pencil object"""

    gpName: StringProperty(default="")
    refLayerName: StringProperty(default="")


class UAS_GreasePencil_FrameTemplate(PropertyGroup):
    """Contains the grease pencil related to the shot"""

    usagePresets: CollectionProperty(type=UAS_ShotManager_FrameUsagePreset)

    def getParentProps(self):
        """return the property settings instance owner of this instance of frame template.
        This can be the general add-on preferences or the props settings from one of the scenes of the file"""
        prefs = config.getAddonPrefs()
        if self == prefs.stb_frameTemplate:
            return prefs

        for scene in bpy.data.scenes:
            if hasattr(scene, "UAS_shot_manager_props"):
                props = config.getAddonProps(scene)
                if self == props.stb_frameTemplate:
                    return props

        return None

    def initialize(self, mode="SCENE"):
        """
        Args:
            mode:   can be SCENE or ADDON_PREFS"
        """
        # self.parent = parent

        _logger.debug_ext(f"Initializing storyboard template preset list for {mode}", col="GREEN", tag="GREASE_PENCIL")
        self.updatePresets(mode=mode)

    def updatePresets(self, mode="SCENE"):
        """
        Args:
            mode:   can be SCENE or ADDON_PREFS"
        """
        _logger.debug_ext(
            f"updatePresets() for storyboard template preset list for {mode}", col="GREEN", tag="GREASE_PENCIL"
        )
        # Can be SCENE or ADDON_PREFS"
        prefs = config.getAddonPrefs()
        if "SCENE" == mode:
            props = config.getAddonProps(bpy.context.scene)
        else:
            props = prefs

        if "ADDON_PREFS" == mode:
            _logger.debug_ext("   In ADDON PREFS Add Presets", col="GREEN", tag="GREASE_PENCIL")
            # initialize the add-on preferences set of presets
            # wkipwkipwkip
            # Canvas
            # _use = True
            # _layerName = "_Canvas_"
            # _matName = "_Canvas_Mat"
            # props.stb_frameTemplate.addPreset("MG_FILLS", _use, _layerName, _matName)
            props.stb_frameTemplate.addPreset("CANVAS")

            # BG #############
            # _use = True
            # _layerName = "BG Fills"
            # _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("BG_FILLS")
            # _use = True
            # _layerName = "BG Lines"
            # _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("BG_LINES")

            # MG #############
            # _use = True
            # _layerName = "MiddleG Fills"
            # _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("MG_FILLS")
            # _use = True
            # _layerName = "MiddleG Lines"
            # _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("MG_LINES")

            # FG #############
            # _use = True
            # _layerName = "FG Fills"
            # _matName = "Stb_Fills"
            props.stb_frameTemplate.addPreset("FG_FILLS")
            # _use = True
            # _layerName = "FG Lines"
            # _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("FG_LINES")

            # persp #############
            # _use = True
            # _layerName = "Perspective"
            # _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("PERSP")

            # rough #############
            # _use = True
            # _layerName = "Rough"
            # _matName = "Stb_Lines"
            props.stb_frameTemplate.addPreset("ROUGH")

        else:
            # SCENE
            # initialize the template presets of the scene from the add-on preferences
            _logger.debug_ext("   In SCENE Add Presets", col="GREEN", tag="GREASE_PENCIL")
            # bpy.ops.uas_shot_manager.greasepencil_template_panel(mode=mode)

            prefsTemplate = prefs.stb_frameTemplate

            def _createPreset(id):
                preset = self.getPresetByID(id)
                if preset is None:
                    preset = self.addPreset(id)
                    # prefsPreset = prefs.stb_frameTemplate.getPresetByID(id)
                    # if prefsPreset is not None:
                    #     preset.used = prefsPreset.used
                    #     preset.label = str(prefsPreset.label)
                    #     preset.layerName = str(prefsPreset.layerName)
                    #     preset.materialName = str(prefsPreset.materialName)
                if preset is not None:
                    # prefsTemplate.getPreset(preset, preset.id, preset.used, preset.layerName, preset.materialName)
                    # prefsTemplate.getPreset(preset, preset.id, "used", "layerName", "materialName")
                    pass

            # order is important
            presets = self.getPresetIDs()
            for p in reversed(presets):
                _createPreset(p)

    def getPresetIDs(self):
        """Return a list with the supported presets"""
        # order is important
        return ["ROUGH", "PERSP", "FG_LINES", "FG_FILLS", "MG_LINES", "MG_FILLS", "BG_LINES", "BG_FILLS", "CANVAS"]

    def getUsedPresets(self):
        """Return a list with the existing used presets"""
        presets = self.getPresetIDs()
        usedPresets = list()
        for presetID in reversed(presets):
            preset = self.getPresetByID(presetID)
            if preset is not None and preset.used:
                usedPresets.append(preset)
        return usedPresets

    def getPresetByID(self, id):
        preset = None
        if len(self.usagePresets):
            for p in self.usagePresets:
                if id == p.id:
                    return p
        return preset

    def addPreset(self, id):
        """Create a new preset and return it
        If a preset with the same ID already exists then it is returned as is
        Args:
            id: Can be anything (nothing hardcoded in SM) but most common are:
                "CANVAS", "BG_LINES", "BG_FILLS", "MG_LINES", "MG_FILLS", "FG_LINES", "FG_FILLS", "PERSP", "ROUGH"
        """
        preset = None
        if "" != id:
            preset = self.getPresetByID(id)
            if preset is None:
                preset = self.usagePresets.add()
                preset.id = id
                self.resetPresetToDefault(preset)

        return preset

    # def addPreset(self, id, used=False, label="", layerName="", materialName="", updateExisting=True):
    #     """Create a new preset and return it
    #     If a preset with the same ID already exists then it is returned as is
    #     Args:
    #         id: Can be anything (nothing hardcoded in SM) but most common are:
    #             "CANVAS", "BG_LINES", "BG_FILLS", "MG_LINES", "MG_FILLS", "FG_LINES", "FG_FILLS", "PERSP", "ROUGH"
    #         updateExisting: if True then use the provided property values to initialize the new preset
    #     """
    #     preset = self.getPresetByID(id)
    #     isNewPreset = False

    #     if preset is None and "" != id:
    #         preset = self.usagePresets.add()
    #         preset.id = id
    #         isNewPreset = True
    #         self.resetPresetToDefault(preset)

    #     if updateExisting:
    #         # preset.id = id
    #         preset.used = used
    #         preset.label = label
    #         preset.layerName = layerName
    #         preset.materialName = materialName

    #     return preset

    # def getPreset(self, prop, id, used, layerName, materialName):
    #     preset = self.getPresetByID(id)
    #     if preset is not None:
    #         setattr(prop, used, preset.used)
    #         setattr(prop, layerName, preset.layerName)
    #         setattr(prop, materialName, preset.materialName)

    def resetAllPresetsToDefault(self):
        _logger.debug_ext(f"wkip Reseting prefs presets in Props.init !!!")

        presets = self.getPresetIDs()
        for presetID in presets:
            preset = self.getPresetByID(presetID)
            if preset is None:
                preset = self.addPreset(presetID)
            else:
                self.resetPresetToDefault(preset)

    def resetPresetToDefaultByID(self, id):
        preset = self.getPresetByID(id)
        self.resetPresetToDefault(preset)

    def resetPresetToDefault(self, preset):
        """Set all the properties (except id) of the provided preset back to their default value"""
        prefs = config.getAddonPrefs()

        # parentProps = self.getParentProps()

        if prefs.stb_frameTemplate == self:
            _logger.debug_ext(f"Resetting preset {preset.id} in the Preferences", col="PURPLE", tag="GREASE_PENCIL")

            if "ROUGH" == preset.id:
                preset.used = True
                preset.label = "Rough"
                preset.layerName = "Rough"
                preset.materialName = "Lines"
            elif "PERSP" == preset.id:
                preset.used = True
                preset.label = "Perspective"
                preset.layerName = "Perspective"
                preset.materialName = "Lines"

            elif "FG_LINES" == preset.id:
                preset.used = True
                preset.label = "Foreground Lines"
                preset.layerName = "FG Lines"
                preset.materialName = "Stb_Lines"
            elif "FG_FILLS" == preset.id:
                preset.used = True
                preset.label = "Foreground Fills"
                preset.layerName = "FG Fills"
                preset.materialName = "Stb_Fills"

            elif "MG_LINES" == preset.id:
                preset.used = True
                preset.label = "Middle-ground Lines"
                preset.layerName = "MiddleG Lines"
                preset.materialName = "Stb_Lines"
            elif "MG_FILLS" == preset.id:
                preset.used = True
                preset.label = "Middle-ground Fills"
                preset.layerName = "MiddleG Fills"
                preset.materialName = "Stb_Fills"

            elif "BG_LINES" == preset.id:
                preset.used = True
                preset.label = "Background Lines"
                preset.layerName = "BG Lines"
                preset.materialName = "Stb_Lines"
            elif "BG_FILLS" == preset.id:
                preset.used = True
                preset.label = "Background Fills"
                preset.layerName = "BG Fills"
                preset.materialName = "Stb_Fills"

            elif "CANVAS" == preset.id:
                preset.used = True
                preset.label = "Canvas"
                preset.layerName = "_Canvas_"
                preset.materialName = "_Canvas_Mat"

        else:
            _logger.debug_ext(
                f"Resetting preset {preset.id} in the scene {bpy.context.scene}", col="PURPLE", tag="GREASE_PENCIL"
            )

            defaulPresetFromPrefs = prefs.stb_frameTemplate.getPresetByID(preset.id)
            if defaulPresetFromPrefs is None:
                defaulPresetFromPrefs = prefs.stb_frameTemplate.addPreset(preset.id)
            preset.used = defaulPresetFromPrefs.used
            preset.label = defaulPresetFromPrefs.label
            preset.layerName = defaulPresetFromPrefs.layerName
            preset.materialName = defaulPresetFromPrefs.materialName

    ###############################
    # frame grid
    ###############################

    frameGrid: PointerProperty(type=UAS_ShotManager_FrameGrid)

    ###############################
    # layers visibility
    ###############################

    # frameGrid: PointerProperty(type=StringProperty)
    layerNameUsedForVisibilityToggle: StringProperty(default="")

    def toggleSoloLayersVisibility(self, gpencil, layerName):
        """Can work on any grease pencil object"""
        if gpencil is None or "GPENCIL" != gpencil.type:
            return
        if layerName in gpencil.data.layers:
            if utils_greasepencil.isLayerVisibile(gpencil, layerName):
                # hide all layers
                # NOTE: should probably hide only supported layers
                if layerName == self.layerNameUsedForVisibilityToggle:
                    # then unhide
                    for layer in gpencil.data.layers:
                        layer.hide = False
                    self.layerNameUsedForVisibilityToggle = ""
                else:
                    # hide
                    for layer in gpencil.data.layers:
                        if layer.info != layerName:
                            layer.hide = True
                    self.layerNameUsedForVisibilityToggle = layerName
            else:
                # we unhide only the layer
                gpencil.data.layers[layerName].hide = False

    ###############################
    # edited grease pencil settings
    ###############################

    editedGPSettings: CollectionProperty(type=UAS_ShotManager_GreasepencilObjSettings)

    def getEditedGPByName(self, gpName):
        """Return the instance of UAS_ShotManager_GreasepencilObjSettings for the grease pencil
        with the specified name, None if the instance is not found"""
        for item in self.editedGPSettings:
            if gpName == item.gpName:
                return item
        return None

    def getEditedGPLayerName(self, gpName, refLayerName):
        """Return the name of the specifed edited grease pencil object, 'ALL' if the object is not found"""
        gpSettings = self.getEditedGPByName(gpName)
        if gpSettings is None:
            # return "ACTIVE"
            return "ALL"
        else:
            return gpSettings.refLayerName

    def storeEditedGPSettings(self, gpName, refLayerName):
        """Update, or add if not found, the settings of the specifed edited grease pencil object
        Return the corresponding settings instance"""
        _logger.debug_ext(f"storeEditedGPSettings: {gpName}{refLayerName}", tag="GREASE_PENCIL")

        if gpName is None or "" == gpName:
            return None
        gpSettings = self.getEditedGPByName(gpName)
        if gpSettings is None:
            gpSettings = self.editedGPSettings.add()
            gpSettings.gpName = gpName
        gpSettings.refLayerName = refLayerName

        return gpSettings


_classes = (
    UAS_ShotManager_GreasepencilObjSettings,
    UAS_GreasePencil_FrameTemplate,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
