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


def set_StampInfoSettings(scene):
    print(" -- * set_StampInfoSettings * --")

    if bpy.context.scene.UAS_StampInfo_Settings is not None:

        props = scene.UAS_shot_manager_props
        stampInfoSettings = scene.UAS_StampInfo_Settings

        stampInfoSettings.stampInfoUsed = scene.UAS_shot_manager_props.useStampInfoDuringRendering

        if stampInfoSettings.stampInfoUsed:

            #####################
            # enable or disable stamp info properties
            #####################
            if props.use_project_settings:
                # wkip get stamp info configuration specifed for the project

                ####################################
                # top
                ####################################

                stampInfoSettings.dateUsed = True
                stampInfoSettings.timeUsed = True
                stampInfoSettings.userNameUsed = True

                stampInfoSettings.videoFrameUsed = True
                stampInfoSettings.videoRangeUsed = True
                stampInfoSettings.videoHandlesUsed = True

                stampInfoSettings.animDurationUsed = True

                # defined per shot?
                #stampInfoSettings.notesUsed = shot.hasNotes()
                #stampInfoSettings.cornerNoteUsed = not shot.enabled


                ####################################
                # bottom
                ####################################

                stampInfoSettings.sceneUsed = True
                stampInfoSettings.takeUsed = True
                #  stampInfoSettings.shotName       = shotName
                stampInfoSettings.shotUsed = True
                stampInfoSettings.cameraUsed = True
                stampInfoSettings.cameraLensUsed = True

                stampInfoSettings.edit3DFrameUsed = True
                stampInfoSettings.edit3DTotalNumberUsed = True
                stampInfoSettings.framerateUsed = True

                stampInfoSettings.shotDurationUsed = True

                stampInfoSettings.filenameUsed = True
                stampInfoSettings.filepathUsed = True

                stampInfoSettings.currentFrameUsed = True
                stampInfoSettings.frameRangeUsed = True
                stampInfoSettings.frameHandlesUsed = True
                # stampInfoSettings.shotHandles = props.handles


                ####################################
                # general
                ####################################

                stampInfoSettings.borderUsed = True
                stampInfoSettings.stampPropertyLabel = False
                stampInfoSettings.stampPropertyValue = True

                stampInfoSettings.debug_DrawTextLines = False

            else:
                # use stamp info settings from scene
                pass

            #####################
            # set the value of stamp info global properties (ie not dependent on current time not on scene state),
            # this independently from their display state set above
            #####################

            if props.use_project_settings:
                projProp_Name = props.project_name

                projProp_resolution_x = props.project_resolution_x
                projProp_resolution_y = props.project_resolution_y
                projProp_resolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

                stampInfoSettings.tmp_stampInfoRenderMode = stampInfoSettings.stampInfoRenderMode
                stampInfoSettings.stampInfoRenderMode = "OUTSIDE"
                stampInfoSettings.stampRenderResYOutside_percentage = (
                    float(projProp_resolutionFramed[1]) / projProp_resolution_y
                ) * 100.0 - 100.0
                
                stampInfoSettings.stampInfoRenderMode = "OVER"
                stampInfoSettings.stampRenderResOver_percentage = 86.0

                stampInfoSettings.automaticTextSize = False
                stampInfoSettings.extPaddingNorm = 0.020
                stampInfoSettings.fontScaleHNorm = 0.0168
                stampInfoSettings.interlineHNorm = 0.0072



                ####################################
                # top
                ####################################

                ############
                # logo

                if "" == props.project_logo_path:
                    # no logo used at all because none specified
                    stampInfoSettings.logoUsed = False
                else:
                    stampInfoSettings.logoUsed = True
                    stampInfoSettings.logoMode = "CUSTOM"
                    stampInfoSettings.logoFilepath = props.project_logo_path

                stampInfoSettings.logoScaleH = 0.05
                stampInfoSettings.logoPosNormX = 0.018
                stampInfoSettings.logoPosNormY = 0.014

                stampInfoSettings.projectName = projProp_Name
                stampInfoSettings.projectUsed = True

                # stampInfoSettings.edit3DFrame = props.     # set in the render loop
                # stampInfoSettings.edit3DTotalNumber = props.getEditDuration()


                ####################################
                # bottom
                ####################################


            else:
                pass

                projProp_resolution_x = scene.render.resolution_x
                projProp_resolution_y = scene.render.resolution_y


            stampInfoSettings.tmp_usePreviousValues = False

            # stampInfoSettings.tmp_previousResolution_x = projProp_resolution_x
            # stampInfoSettings.tmp_previousResolution_y = projProp_resolution_y

            # stampInfoSettings.tmp_stampRenderResYDirToCompo_percentage = (
            #     stampInfoSettings.stampRenderResYDirToCompo_percentage
            # )



