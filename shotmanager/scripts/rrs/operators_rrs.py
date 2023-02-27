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
To do: module description here.
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, IntProperty

from shotmanager.config import config

from . import publish_rrs

# To call the operator:
# bpy.ops.uas_shot_manager.initialize_rrs_project(override_existing = True, verbose = True)
# Fix old data by filling the entities parents
class UAS_FixEntitiesParent(Operator):
    bl_idname = "uas_shot_manager.fix_entities_parent"
    bl_label = "Fix Parents"
    bl_description = "Initialize scene for RRS project"

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.getParentScene()
        for t in props.takes:
            t.getParentScene()
        return {"FINISHED"}


# To call the operator:
# bpy.ops.uas_shot_manager.initialize_rrs_project(override_existing = True, verbose = True)
class UAS_InitializeRRSProject(Operator):
    bl_idname = "uas_shot_manager.initialize_rrs_project"
    bl_label = "Initialize scene for RRS project"
    bl_description = "Initialize scene for RRS project"

    override_existing: BoolProperty(default=False)
    verbose: BoolProperty(default=False)

    def execute(self, context):
        print(" UAS_InitializeRRSProject")

        publish_rrs.initializeForRRS(self.override_existing, verbose=self.verbose)

        return {"FINISHED"}


# To call the operator:
# bpy.ops.uas_shot_manager.lauch_rrs_render(prodFilePath = "c:\\tmpRezo\\" + context.scene.name + "\\",
# verbose = True, takeIndex = -1)
# use takeIndex = -1 to render the current take
class UAS_LaunchRRSRender(Operator):
    bl_idname = "uas_shot_manager.lauch_rrs_render"
    bl_label = "RRS Render Script"
    bl_description = "Run the RRS Render Script used for the scene publish"

    prodFilePath: StringProperty(default="")
    takeIndex: IntProperty(default=-1)
    verbose: BoolProperty(default=False)
    useCache: BoolProperty(default=False)

    def execute(self, context):
        """Launch RRS Publish script"""
        print(" UAS_LaunchRRSRender")

        props = config.getAddonProps(context.scene)
        settingsDict = dict()
        settingsDict["publish_rendering_file"] = "C:\\my rendering file.blend"
        settingsDict["publish_step"] = "Cleaning"

        if not props.sceneIsReady():
            return {"CANCELLED"}

        if props.rrs_useRenderRoot:  # used in SM UI in the debug panel
            print("Publish at render root")
            publish_rrs.publishRRS(
                bpy.path.abspath(props.renderRootPath),
                verbose=True,
                takeIndex=self.takeIndex,
                useCache=False,
                fileListOnly=props.rrs_fileListOnly,
                rerenderExistingShotVideos=props.rrs_rerenderExistingShotVideos,
                renderAlsoDisabled=props.rrs_renderAlsoDisabled,
                settingsDict=settingsDict,
            )
        else:
            publish_rrs.publishRRS(
                self.prodFilePath,
                verbose=self.verbose,
                takeIndex=self.takeIndex,
                useCache=self.useCache,
                fileListOnly=props.rrs_fileListOnly,
                rerenderExistingShotVideos=props.rrs_rerenderExistingShotVideos,
                renderAlsoDisabled=props.rrs_renderAlsoDisabled,
                settingsDict=settingsDict,
            )

        print("End of Publish")

        return {"FINISHED"}
