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
Shot Manager debug tools and functions
"""

import bpy

from bpy.types import Operator
from bpy.props import StringProperty
from ..config import config


class UAS_Debug_RunFunction(Operator):
    bl_idname = "uas.debug_runfunction"
    bl_label = "fff"
    bl_description = ""

    functionName: StringProperty()

    def execute(self, context):
        print("\n----------------------------------------------------")
        print("\nUAS_Debug_RunFunction: ", self.functionName)
        print("\n")

        if "parseOtioFile" == self.functionName:
            from ..otio.otio_wrapper import parseOtioFile
            from ..otio.imports import getSequenceListFromOtio

            otioFile = (
                r"Z:\EvalSofts\Blender\DevPython_Data\UAS_ShotManager_Data\ImportEDLPremiere\ImportEDLPremiere.xml"
            )
            otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
            #  otioFile = r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
            # getSequenceListFromOtio(otioFile)
            # parseOtioFile(otioFile)

        return {"FINISHED"}


class UAS_MotionTrackingTab(Operator):
    bl_idname = "uas.motiontrackingtab"
    bl_label = "fff"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print(" Open VSE")
        #    getSceneVSE(bpy.context.scene.name)
        # getSceneMotionTracking(bpy.context.scene.name)

        previousType = bpy.context.area.ui_type
        bpy.context.area.ui_type = "SEQUENCE_EDITOR"

        bpy.context.object.data.background_images[0].clip.use_proxy = True
        bpy.context.object.data.background_images[0].clip.proxy.build_50 = True

        bpy.context.object.data.background_images[0].clip_user.proxy_render_size = "PROXY_50"

        for area in bpy.context.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                ctx = bpy.context.copy()
                # ctx = {"area": area}
                ctx["area"] = area
                # bpy.ops.clip.rebuild_proxy("EXEC_AREA")
                bpy.ops.sequencer.rebuild_proxy(ctx)
                break

        # bpy.context.area.ui_type = "CLIP_EDITOR"
        # # bpy.context.object.data.background_images[0].clip.proxy
        # # ctx = bpy.context.copy()
        # # ctx["area"] = bpy.context.area
        # bpy.ops.clip.rebuild_proxy()

        bpy.context.area.ui_type = previousType

        # bpy.context.object.data.proxy_render_size = 'PROXY_25'

        return {"FINISHED"}


_classes = (
    UAS_MotionTrackingTab,
    UAS_Debug_RunFunction,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    config.devDebug = False
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
