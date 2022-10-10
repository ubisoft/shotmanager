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
Retimer properties
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, PointerProperty

from .retimer_retime_engine import UAS_Retimer_RetimeEngine
from .retimer_applyto_settings import UAS_Retimer_ApplyToSettings

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_Retimer_Properties(PropertyGroup):

    retimeEngine: PointerProperty(
        type=UAS_Retimer_RetimeEngine,
    )

    def list_retime_applyto_modes(self, context):
        items = list()

        items.append(
            (
                "SCENE",
                "Whole Scene",
                "The retime will be globaly applied to the scene. Every entity associated to time\nmay be affected",
            ),
        )

        # (
        #     "STORYBOARD",
        #     "Storyboard",
        #     "Only the shots of type 'Storyboard' will be retimed. The content of the scene is NOT affected",
        #     1,
        # ),
        items.append(
            ("SELECTED_OBJECTS", "Selected Objects", "Retime only the selected objects"),
        )
        if config.devDebug:
            items.append(
                ("LEGACY", "Legacy Settings", "Use the settings exposed in the previous versions of Shot Manager"),
            )

        return items

    def _update_applyTo(self, context):
        self.initialize()

    applyTo: EnumProperty(
        name="Apply To",
        description="Defines the context and entities to which the retiming will be applied to",
        items=list_retime_applyto_modes,
        update=_update_applyTo,
        default=0,
    )

    applyToSettingsScene: PointerProperty(
        type=UAS_Retimer_ApplyToSettings,
    )
    applyToSettingsSelectedObjects: PointerProperty(
        type=UAS_Retimer_ApplyToSettings,
    )
    applyToSettingsLegacy: PointerProperty(
        type=UAS_Retimer_ApplyToSettings,
    )

    def initialize(self):
        self.createRenderSettings()

    def getCurrentApplyToSettings(self):
        if "SCENE" == self.applyTo:
            return self.applyToSettingsScene
        if "SELECTED_OBJECTS" == self.applyTo:
            return self.applyToSettingsSelectedObjects
        if "LEGACY" == self.applyTo:
            return self.applyToSettingsLegacy
        return None

    def createRenderSettings(self):
        # _logger.debug_ext("createRenderSettings", col="GREEN", tag="RENDER")

        self.applyToSettingsScene.initialize("SCENE")
        self.applyToSettingsSelectedObjects.initialize("SELECTED_OBJECTS")
        self.applyToSettingsLegacy.initialize("LEGACY")

    def getQuickHelp(self, topic):
        if -1 != topic.find("APPLYTO_"):
            retimerSettings = self.getCurrentApplyToSettings()
            return retimerSettings.getQuickHelp(topic)
        else:
            return self.retimeEngine.getQuickHelp(topic)


_classes = (
    UAS_Retimer_ApplyToSettings,
    UAS_Retimer_RetimeEngine,
    UAS_Retimer_Properties,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
