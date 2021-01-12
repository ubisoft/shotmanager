import bpy


def set_StampInfoSettings(scene):
    print(" -- * set_StampInfoSettings * --")

    if bpy.context.scene.UAS_StampInfo_Settings is not None:

        props = scene.UAS_shot_manager_props
        stampInfoSettings = scene.UAS_StampInfo_Settings

        stampInfoSettings.stampInfoUsed = scene.UAS_shot_manager_props.useStampInfoDuringRendering

        if stampInfoSettings.stampInfoUsed:

            projProp_Name = props.project_name

            projProp_resolution_x = scene.render.resolution_x
            projProp_resolution_y = scene.render.resolution_y

            if props.use_project_settings:
                projProp_resolution_x = props.project_resolution_x
                projProp_resolution_y = props.project_resolution_y

            stampInfoSettings.tmp_usePreviousValues = True

            stampInfoSettings.tmp_previousResolution_x = projProp_resolution_x
            stampInfoSettings.tmp_previousResolution_y = projProp_resolution_y

            stampInfoSettings.tmp_stampRenderResYDirToCompo_percentage = (
                stampInfoSettings.stampRenderResYDirToCompo_percentage
            )
            stampInfoSettings.stampRenderResYDirToCompo_percentage = 75.0

            stampInfoSettings.tmp_stampInfoRenderMode = stampInfoSettings.stampInfoRenderMode
            stampInfoSettings.stampInfoRenderMode = "DIRECTTOCOMPOSITE"

            stampInfoSettings.stampPropertyLabel = False
            stampInfoSettings.stampPropertyValue = True

            stampInfoSettings.automaticTextSize = False
            stampInfoSettings.extPaddingNorm = 0.020
            stampInfoSettings.fontScaleHNorm = 0.0168
            stampInfoSettings.interlineHNorm = 0.0072

            ####################################
            # top
            ####################################

            ############
            # logo

            if props.use_project_settings:
                if "" == props.project_logo_path:
                    # no logo used at all because none specified
                    stampInfoSettings.logoUsed = False
                else:
                    stampInfoSettings.logoUsed = True
                    stampInfoSettings.logoMode = "CUSTOM"
                    stampInfoSettings.logoFilepath = props.project_logo_path
            else:
                # wkip use the scene stamp info settings ??
                stampInfoSettings.logoUsed = True
                stampInfoSettings.logoMode = "BUILTIN"
                stampInfoSettings.logoBuiltinName = "Blender_Logo.png"

            stampInfoSettings.logoScaleH = 0.05
            stampInfoSettings.logoPosNormX = 0.018
            stampInfoSettings.logoPosNormY = 0.014

            stampInfoSettings.projectName = projProp_Name
            stampInfoSettings.projectUsed = False

            stampInfoSettings.dateUsed = True
            stampInfoSettings.timeUsed = True

            stampInfoSettings.videoDurationUsed = True

            stampInfoSettings.videoFrameUsed = True
            stampInfoSettings.videoRangeUsed = True
            stampInfoSettings.videoHandlesUsed = True

            stampInfoSettings.edit3DFrameUsed = True
            # stampInfoSettings.edit3DFrame = props.     # set in the render loop
            stampInfoSettings.edit3DTotalNumberUsed = True
            # stampInfoSettings.edit3DTotalNumber = props.getEditDuration()

            stampInfoSettings.framerateUsed = True

            ####################################
            # bottom
            ####################################

            stampInfoSettings.sceneUsed = True
            stampInfoSettings.takeUsed = True
            #  stampInfoSettings.shotName       = shotName
            stampInfoSettings.shotUsed = True
            stampInfoSettings.cameraUsed = True
            stampInfoSettings.cameraLensUsed = True

            stampInfoSettings.shotDurationUsed = False

            stampInfoSettings.filenameUsed = True
            stampInfoSettings.filepathUsed = True

            stampInfoSettings.currentFrameUsed = True
            stampInfoSettings.frameRangeUsed = True
            stampInfoSettings.frameHandlesUsed = True
            # stampInfoSettings.shotHandles = props.handles

            stampInfoSettings.debug_DrawTextLines = False

