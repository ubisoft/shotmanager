# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
Rendering code
"""

import os
from pathlib import Path

import bpy
from bpy.types import Operator

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def isRenderPathValid(scene):
    filepath = bpy.path.abspath(scene.render.filepath)

    head, tail = os.path.split(filepath)

    filePathIsValid = os.path.exists(head)

    return filePathIsValid


def getRenderOutputFilename(scene, fileNameOnly=False):
    """
    Return the list of the files that are to be rendered by the scene, according to the settings of the specified scene
    """
    outputFiles = list()

    filePath = bpy.path.abspath(scene.render.filepath)

    # print("\n *** images defs:")
    # print(f"   From {scene.frame_start} to {scene.frame_end} by {scene.frame_step}")

    # note that as strange as the results can be this code perfectly replicates (as far as tested) the
    # behavior of Blender in terms of file naming
    for i in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):

        fileName = Path(filePath).stem
        # print(f"fileName: {fileName}")
        firstDigitIndex = fileName.find("#")
        # print(f"firstDigitIndex: {firstDigitIndex}")
        genericFileName = ""
        if -1 != firstDigitIndex:
            numDigits = 0
            digitIndex = firstDigitIndex
            while digitIndex < len(fileName) and "#" == fileName[digitIndex]:
                numDigits += 1
                digitIndex += 1
            # print(f"numDigits: {numDigits}")
            genericFileName = fileName[0:firstDigitIndex] + "{number:0{width}d}".format(width=numDigits, number=i)
            if not scene.render.use_file_extension:
                genericFileName += f"{Path(filePath).suffix}"
        else:
            genericFileName = str(Path(filePath).name) + "{number:0{width}d}".format(width=4, number=i)

        # explicit file extension
        if scene.render.use_file_extension:
            genericFileName += f".{(scene.render.image_settings.file_format).lower()}"

        defFileName = ""
        if not fileNameOnly:
            defFileName += str(Path(filePath).parent) + "\\"
        defFileName += genericFileName

        print(f"      - {defFileName}")
        outputFiles.append(defFileName)

    return outputFiles


class Utils_LaunchRender(Operator):
    bl_idname = "utils.launch_render"
    bl_label = "Render"
    bl_description = "Render"
    bl_options = {"INTERNAL"}

    renderMode: bpy.props.EnumProperty(
        name="Render", description="", items=(("STILL", "Still", ""), ("ANIMATION", "Animation", "")), default="STILL"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def execute(self, context):

        if "STILL" == self.renderMode:
            #     bpy.ops.render.view_show()
            #     bpy.ops.render.render(use_viewport = True)
            bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=False)
        elif "ANIMATION" == self.renderMode:

            bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

            # en bg, ne s'arrete pas
            # bpy.ops.render.render(animation = True)

            # bpy.ops.render.opengl ( animation = True )

        return {"FINISHED"}
