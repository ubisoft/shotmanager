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
Output settings
"""

import bpy

from bpy.types import PropertyGroup
from bpy.props import IntProperty, BoolProperty

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_OutputParams_Resolution(PropertyGroup):
    def copyPropertiesFrom(self, source):
        """
        Copy properties from the specified source to this one
        """
        self.resolution_x = source.resolution_x
        self.resolution_y = source.resolution_y
        self.resolution_framed_x = source.resolution_framed_x
        self.resolution_framed_y = source.resolution_framed_y

        self.useStampInfoDuringRendering = source.useStampInfoDuringRendering

    def _update_resolution(self, context):
        props = config.getAddonProps(bpy.context.scene)
        if props is not None:
            if self == props.getCurrentTake().outputParams_Resolution:
                props.setResolutionToScene()

    def _get_resolution_x(self):
        val = self.get("resolution_x", -1)
        if -1 == val:
            props = config.getAddonProps(bpy.context.scene)
            if props is not None:
                val = props.parentScene.render.resolution_x
        return val

    def _set_resolution_x(self, value):
        self["resolution_x"] = value

    resolution_x: IntProperty(
        name="Res. X", min=0, default=-1, get=_get_resolution_x, set=_set_resolution_x, update=_update_resolution
    )

    def _get_resolution_y(self):
        val = self.get("resolution_y", -1)
        if -1 == val:
            props = config.getAddonProps(bpy.context.scene)
            if props is not None:
                val = props.parentScene.render.resolution_y
        return val

    def _set_resolution_y(self, value):
        self["resolution_y"] = value

    resolution_y: IntProperty(
        name="Res. Y", min=0, default=-1, get=_get_resolution_y, set=_set_resolution_y, update=_update_resolution
    )

    resolution_framed_x: IntProperty(name="Res. Framed X", min=0, default=-1)
    resolution_framed_y: IntProperty(name="Res. Framed Y", min=0, default=-1)

    def get_useStampInfoDuringRendering(self):
        #  return self.useStampInfoDuringRendering
        val = self.get("useStampInfoDuringRendering", True)
        # print("*** get_useStampInfoDuringRendering: value: ", val)
        return val

    def set_useStampInfoDuringRendering(self, value):
        print("*** set_useStampInfoDuringRendering: value: ", value)
        self["useStampInfoDuringRendering"] = value

        if getattr(bpy.context.scene, "UAS_SM_StampInfo_Settings", None) is not None:
            # bpy.context.scene.UAS_SM_StampInfo_Settings.activateStampInfo(value)
            bpy.context.scene.UAS_SM_StampInfo_Settings.stampInfoUsed = value

    useStampInfoDuringRendering: BoolProperty(
        name="Stamp Info on Output",
        description="Stamp render information on rendered images thanks to Ubisoft Stamp Info add-on",
        default=True,
        get=get_useStampInfoDuringRendering,  # removed cause the use of Stamp Info in this add-on is independent from the one of Stamp Info add-on itself
        set=set_useStampInfoDuringRendering,
        options=set(),
    )

    def draw(self, context, ui_component, enabled=True):
        props = config.getAddonProps(context.scene)

        ui_component.enabled = enabled

        split = ui_component.split(factor=0.3, align=False)
        split.label(text="Resolution")
        row = split.row(align=False)
        row.use_property_split = False
        row.alignment = "RIGHT"
        row.prop(self, "resolution_x", text="Width:")
        row.prop(self, "resolution_y", text="Height:")

        col = ui_component.column(align=False)
        col.separator(factor=0.5)
        colRow = col.split(factor=0.4)
        stampInfoStr = " Use Stamp Info"
        colRow.prop(self, "useStampInfoDuringRendering", text=stampInfoStr)
        if props is not None and not props.isStampInfoAvailable():
            subColRow = colRow.row()
            col.enabled = False
            subColRow.alert = True
            subColRow.alignment = "RIGHT"
            subColRow.label(text="*** Add-on not found ***")

        colRow = col.row()
        colRow.enabled = self.useStampInfoDuringRendering
        split = colRow.split(factor=0.3, align=False)
        row = split.row(align=False)
        row.separator(factor=1.8)
        row.label(text="Frame Resolution")
        row = split.row(align=False)
        row.use_property_split = False
        row.alignment = "RIGHT"
        row.prop(self, "resolution_framed_x", text="Width:")
        row.prop(self, "resolution_framed_y", text="Height:")
