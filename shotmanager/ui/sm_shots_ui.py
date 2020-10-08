import json

import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty

from shotmanager.config import config
from shotmanager.utils import utils

import logging

_logger = logging.getLogger(__name__)


#############
# Shot Item
#############


class UAS_UL_ShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = context.scene.UAS_shot_manager_props
        current_shot_index = props.current_shot_index

        itemHasWarnings = False

        cam = "Cam" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        # check if the camera still exists in the scene
        cameraIsValid = item.isCameraValid()
        itemHasWarnings = not cameraIsValid

        # draw the Duration components

        if item.enabled:
            icon = config.icons_col[f"ShotMan_Enabled{cam}"]
            if item.start <= context.scene.frame_current <= item.end:
                icon = config.icons_col[f"ShotMan_EnabledCurrent{cam}"]
        else:
            icon = config.icons_col[f"ShotMan_Disabled{cam}"]

        if item.camera is None or itemHasWarnings:
            layout.alert = True

        row = layout.row()

        row.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index

        if props.display_selectbut_in_shotlist or props.display_color_in_shotlist:
            row = layout.row(align=True)
            row.scale_x = 1.0
            if props.display_selectbut_in_shotlist:
                row.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index

            if props.display_notes_in_properties and props.display_notes_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.0

                if item.hasNotes():
                    notesIcon = "ALIGN_TOP"
                    notesIcon = "ALIGN_JUSTIFY"
                    notesIcon = "WORDWRAP_OFF"
                    notesIcon = "WORDWRAP_OFF"
                    # notesIcon = "TEXT"
                    # notesIcon = "OUTLINER_DATA_GP_LAYER"
                    row.operator("uas_shot_manager.shots_shownotes", text="", icon=notesIcon).index = index
                else:
                    notesIcon = "WORDWRAP_ON"
                    notesIcon = "MESH_PLANE"
                    row.operator("uas_shot_manager.shots_shownotes", text="", icon=notesIcon).index = index
                    # emptyIcon = config.icons_col["General_Empty_32"]
                    # row.operator(
                    #     "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
                    # ).index = index
                row.scale_x = 0.9

            if props.display_color_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 0.2
                row.prop(item, "color", text="")
                row.scale_x = 0.45

        row = layout.row(align=True)

        row.scale_x = 1.0
        if props.display_enabled_in_shotlist:
            row.prop(item, "enabled", text="")
            row.separator(factor=0.9)
        row.scale_x = 0.8
        row.label(text=item.name)

        ###########
        # shot values
        ###########

        row = layout.row(align=True)
        row.scale_x = 2.0
        grid_flow = row.grid_flow(align=True, columns=7, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        # currentFrameInEdit = props.
        # start
        ###########
        if props.display_edit_times_in_shotlist:
            # grid_flow.scale_x = button_x_factor
            # if props.display_getsetcurrentframe_in_shotlist:
            #     grid_flow.operator(
            #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
            #     ).shotSource = f"[{index},0]"

            grid_flow.scale_x = 0.4
            shotEditStart = item.getEditStart()
            if currentFrame == item.start:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            # grid_flow.prop(item, "start", text="")
            # grid_flow.label(text=str(shotDuration))
            grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditStart)).shotSource = f"[{index},0]"
            grid_flow.alert = False
        else:
            grid_flow.scale_x = button_x_factor
            if props.display_getsetcurrentframe_in_shotlist:
                grid_flow.operator(
                    "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                ).shotSource = f"[{index},0]"

            grid_flow.scale_x = 0.4
            if currentFrame == item.start:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.prop(item, "start", text="")
            grid_flow.alert = False

        # duration
        ###########

        # display_duration_after_time_range
        if not props.display_duration_after_time_range:
            grid_flow.scale_x = button_x_factor - 0.1
            grid_flow.prop(
                item,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            if (
                item.start < currentFrame
                and currentFrame < item.end
                or (item.start == item.end and currentFrame == item.start)
            ):
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True

            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 0.3
                grid_flow.prop(item, "duration_fp", text="")
            else:
                grid_flow.scale_x = 0.05
                grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
            grid_flow.alert = False
        else:
            grid_flow.scale_x = 1.5

        # end
        ###########
        if props.display_edit_times_in_shotlist:
            grid_flow.scale_x = 0.4
            shotEditEnd = item.getEditEnd()
            if currentFrame == item.end:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditEnd)).shotSource = f"[{index},1]"
            grid_flow.alert = False

            # grid_flow.scale_x = button_x_factor - 0.2
            # if props.display_getsetcurrentframe_in_shotlist:
            #     grid_flow.operator(
            #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
            #     ).shotSource = f"[{index},1]"
        else:
            grid_flow.scale_x = 0.4
            if currentFrame == item.end:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.prop(item, "end", text="")
            grid_flow.alert = False

            grid_flow.scale_x = button_x_factor - 0.2
            if props.display_getsetcurrentframe_in_shotlist:
                grid_flow.operator(
                    "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                ).shotSource = f"[{index},1]"

        if props.display_duration_after_time_range:
            row = layout.row(align=True)
            grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
            grid_flow.use_property_split = False
            # grid_flow.scale_x = button_x_factor - 0.1
            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 1.5
            grid_flow.prop(
                item,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            if (
                item.start < currentFrame
                and currentFrame < item.end
                or (item.start == item.end and currentFrame == item.start)
            ):
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True

            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 0.6
                grid_flow.prop(item, "duration_fp", text="")
            else:
                pass
                # grid_flow.scale_x = 0.1
                # grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
            grid_flow.alert = False

        # camera
        ###########
        row = layout.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
        grid_flow.use_property_split = False
        grid_flow.scale_x = 1.0

        if props.display_camera_in_shotlist:
            if item.camera is None:
                grid_flow.alert = True
            grid_flow.prop(item, "camera", text="")
            if item.camera is None:
                grid_flow.alert = False

        if props.display_lens_in_shotlist:
            grid_flow.scale_x = 0.4
            grid_flow.use_property_decorate = True
            if item.camera is not None:
                grid_flow.prop(item.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="-").index = index
                grid_flow.alert = False
            grid_flow.scale_x = 1.0


##################
# shot properties
##################


class UAS_PT_ShotManager_ShotProperties(Panel):
    bl_label = " "  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shot_Prefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    tmpBGPath: StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)
        val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot
        val = val and not props.dontRefreshUI()
        return val

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        propertiesModeStr = "Current Shot Properties"
        if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
            propertiesModeStr = "Selected Shot Properties"
        row.label(text=propertiesModeStr)

    def draw_header_preset(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid

        if itemHasWarnings:
            self.layout.alert = True
            self.layout.label(text="*** Warning: Camera not in scene !*** ")

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        iconExplorer = config.icons_col["General_Explorer_32"]

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)

        layout = self.layout
        layout.use_property_decorate = False

        if shot is not None:
            box = layout.box()
            box.use_property_decorate = False

            currentTakeInd = props.getCurrentTakeIndex()
            if config.uasDebug:
                row = box.row()
                row.label(
                    text=(
                        f"Current Take Ind: {currentTakeInd}, shot.getParentTakeIndex(): {shot.getParentTakeIndex()}      -       shot.parentScene: {shot.parentScene}"
                        # f"Current Take Ind: {currentTakeInd}, Shot Parent Take Ind: {shot.parentTakeIndex}, shot.getParentTakeIndex(): {shot.getParentTakeIndex()}"
                    )
                )
            # elif currentTakeInd != shot.parentTakeIndex:
            #     row = box.row()
            #     row.alert = True
            #     row.label(
            #         text=(
            #             f"!!! Error: Current Take Index is {currentTakeInd}, Shot Parent Take Index is: {shot.parentTakeIndex} !!!"
            #         )
            #     )

            # name and color
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.prop(shot, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            grid_flow.prop(shot, "color", text="")
            #   grid_flow.scale_x = 1.0
            grid_flow.prop(props, "display_color_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # Duration
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=True, columns=4, even_columns=False)
            # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )
            grid_flow.label(text="Duration: ")

            grid_flow.use_property_split = False
            grid_flow.prop(
                shot,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if shot.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            grid_flow.prop(shot, "duration_fp", text="")

            #    grid_flow.label(text=str(shot.getDuration()) + " frames")
            grid_flow.prop(props, "display_duration_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # camera and lens

            cameraIsValid = shot.isCameraValid()

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            if not cameraIsValid:
                grid_flow.alert = True
            grid_flow.prop(shot, "camera", text="Camera")
            if not cameraIsValid:
                grid_flow.alert = False
            grid_flow.prop(props, "display_camera_in_shotlist", text="")

            # c.separator( factor = 0.5 )   # prevents stange look when panel is narrow
            grid_flow.scale_x = 0.7
            #     row.label ( text = "Lens: " )
            grid_flow.use_property_decorate = True
            if not cameraIsValid:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="No Lens")
                grid_flow.alert = False
            else:
                grid_flow.prop(shot.camera.data, "lens", text="Lens")
            grid_flow.scale_x = 1.0
            grid_flow.prop(props, "display_lens_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents strange look when panel is narrow

            box.separator(factor=0.5)

            # Output
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            grid_flow.label(text="Output: ")
            grid_flow.label(
                text="<Render Root Path> \\ "
                + shot.getParentTake().getName_PathCompliant()
                + " \\ "
                + shot.getOutputMediaPath(providePath=False)
            )
            grid_flow.operator(
                "uas_shot_manager.open_explorer", emboss=True, icon_value=iconExplorer.icon_id, text=""
            ).path = shot.getOutputMediaPath()
            row.separator(factor=0.5)  # prevents strange look when panel is narrow

            # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

            # Notes
            ######################
            if props.display_notes_in_properties:
                box = layout.box()
                box.use_property_decorate = False
                row = box.row()
                row.separator(factor=1.0)
                c = row.column()
                # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
                subrow = c.row()
                subrow.label(text="Notes:")
                subrow.prop(props, "display_notes_in_shotlist", text="")
                subrow.separator(factor=0.5)  # prevents strange look when panel is narrow
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note01", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note02", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note03", text="")
                row.separator(factor=1.0)
                box.separator(factor=0.1)

            # Camera background images
            ######################

            if props.display_camerabgtools_in_properties and shot.camera is not None:
                box = layout.box()
                box.use_property_decorate = False
                row = box.row()
                row.separator(factor=1.0)
                c = row.column()
                grid_flow = c.grid_flow(align=True, columns=4, even_columns=False)

                # grid_flow.prop(shot.camera.data.background_images[0].clip.name)
                if len(shot.camera.data.background_images) and shot.camera.data.background_images[0].clip is not None:
                    grid_flow.prop(shot.camera.data.background_images[0].clip, "filepath")
                else:
                    # tmpBGPath
                    grid_flow.operator(
                        "uas_shot_manager.openfilebrowser_for_cam_bg", text="", icon="FILEBROWSER", emboss=True
                    ).pathProp = "inputOverMediaPath"

                grid_flow.operator(
                    "uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True
                ).shotIndex = props.getShotIndex(shot)

                row = box.row()
                if not len(shot.camera.data.background_images):
                    row.enabled = False
                row.separator(factor=1.0)
                row.prop(shot, "bgImages_linkToShotStart")
                row.prop(shot, "bgImages_offset")


class UAS_PT_ShotManager_ShotsGlobalSettings(Panel):
    bl_label = "Shots Global Control"  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shots_GlobalSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = props.display_camerabgtools_in_properties and len(props.getTakes()) and len(props.get_shots())
        val = val and not props.dontRefreshUI()
        return val

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout = self.layout
        layout.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # Camera background images
        ######################

        if props.display_camerabgtools_in_properties:

            layout.label(text="Camera Background Images:")

            box = layout.box()
            box.use_property_decorate = False

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
            grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            c.enabled = False
            c.prop(props.shotsGlobalSettings, "proxyRenderSize")

            c = row.column()
            c.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

            # c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            # grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

            # grid_flow.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

            row.separator(factor=0.5)  # prevents stange look when panel is narrow


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_OpenFileBrowserForCamBG(Operator):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uas_shot_manager.openfilebrowser_for_cam_bg"
    bl_label = "Camera Background"
    bl_description = "Open a file browser to define the image or video to use as camera background"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    pathProp: StringProperty()

    filepath: StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(default="*.mov;*.mp4", options={"HIDDEN"})

    def invoke(self, context, event):  # See comments at end  [1]

        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        #  filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        props = context.scene.UAS_shot_manager_props
        shot = props.getCurrentShot()

        # start frame of the background video is not set here since it will be linked to the shot start frame
        utils.add_background_video_to_cam(
            shot.camera.data, str(self.filepath), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
        )

        shot.bgImages_linkToShotStart = shot.bgImages_linkToShotStart
        shot.bgImages_offset = shot.bgImages_offset

        return {"FINISHED"}


#################
# tools for shots
#################


class UAS_MT_ShotManager_Shots_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_shots_toolsmenu"
    bl_label = "Shots Tools"
    bl_description = "Shots Tools"

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.create_shots_from_each_camera", icon="ADD")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.create_n_shots", icon="ADD")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shot_duplicates_to_other_take", icon="DUPLICATE")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove Disabled Shots...", icon="REMOVE")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove All Shots...", icon="REMOVE").action = "ALL"

        layout.separator()

        # tools for shots ###
        row = layout.row(align=True)
        row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.unique_cameras")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shots_removecamera")

        # import shots ###

        layout.separator()
        row = layout.row(align=True)
        row.label(text="Import Shots:")

        if config.uasDebug:
            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.operator("uasotio.openfilebrowser", text="Create Shots From EDL").importMode = "CREATE_SHOTS"

        row = layout.row(align=True)
        #    row.operator_context = "INVOKE_DEFAULT"

        #############
        # Predec settings:
        argsDictPredecAct01 = dict()
        argsDictPredecAct01.update(
            {
                "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730.xml"
            }
        )
        argsDictPredecAct01.update({"conformMode": "CREATE"})
        argsDictPredecAct01.update({"mediaHaveHandles": False})
        argsDictPredecAct01.update({"mediaHandlesDuration": 0})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Predec Act 01"
        ).opArgs = json.JSONEncoder().encode(argsDictPredecAct01)

        row = layout.row(align=True)
        #    row.operator_context = "INVOKE_DEFAULT"

        #############
        # Previz settings:
        argsDictPrevAct01 = dict()
        argsDictPrevAct01.update({"otioFile": r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml"})
        argsDictPrevAct01.update({"conformMode": "UPDATE"})
        argsDictPrevAct01.update({"mediaHaveHandles": props.areShotHandlesUsed()})
        argsDictPrevAct01.update({"mediaHandlesDuration": props.getHandlesDuration()})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Previz Act 01"
        ).opArgs = json.JSONEncoder().encode(argsDictPrevAct01)

        layout.separator()

        row = layout.row(align=True)
        #    row.operator_context = "INVOKE_DEFAULT"

        #############
        # Predec settings:
        argsDictPredecAct02 = dict()
        argsDictPredecAct02.update(
            {
                "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act02\Exports\RRSpecial_Act02_AQ_XML_200929\RRspecial_Act02_AQ_200929.xml"
            }
        )
        argsDictPredecAct02.update({"conformMode": "CREATE"})
        argsDictPredecAct02.update({"mediaHaveHandles": props.areShotHandlesUsed()})
        argsDictPredecAct02.update({"mediaHandlesDuration": props.getHandlesDuration()})
        argsDictPredecAct02.update({"mediaHaveHandles": False})
        argsDictPredecAct02.update({"mediaHandlesDuration": 0})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Predec Act 02"
        ).opArgs = json.JSONEncoder().encode(argsDictPredecAct02)

        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug")

        if config.uasDebug:
            row = layout.row(align=True)

            argsDictRefDebug = dict()
            argsDictRefDebug.update(
                {
                    "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\PredecAct01_To40_RefDebug.xml"
                }
            )
            argsDictRefDebug.update({"conformMode": "CREATE"})

            row.operator(
                "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug 40"
            ).opArgs = json.JSONEncoder().encode(argsDictRefDebug)

            row = layout.row(align=True)
            argsDictDebugModifs = dict()
            argsDictDebugModifs.update(
                {
                    #    "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_To40_RefDebug_SwapSeq30_20-30.xml"
                    "otioFile": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\Act01_Seq0060_Main_Take_ModifsSwap.xml"
                }
            )
            argsDictDebugModifs.update({"conformMode": "UPDATE"})
            argsDictDebugModifs.update({"mediaHaveHandles": props.areShotHandlesUsed()})
            argsDictDebugModifs.update({"mediaHandlesDuration": props.getHandlesDuration()})

            row.operator(
                "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug swap"
            ).opArgs = json.JSONEncoder().encode(argsDictDebugModifs)
            # row.operator(
            #     "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug 40 swap"
            # ).otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_To40_RefDebug_SwapSeq30_20-30.xml"  # _to40

        # tools for precut ###
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Tools for Precut:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.predec_shots_from_single_cam")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.print_montage_info")


classes = (
    UAS_UL_ShotManager_Items,
    UAS_PT_ShotManager_ShotProperties,
    UAS_PT_ShotManager_ShotsGlobalSettings,
    UAS_MT_ShotManager_Shots_ToolsMenu,
    UAS_ShotManager_OpenFileBrowserForCamBG,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

