import json

import bpy
from bpy.types import Menu

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

        if (
            props.display_selectbut_in_shotlist
            or props.display_color_in_shotlist
            or props.display_cameraBG_in_shotlist
            or props.display_greasepencil_in_shotlist
        ):
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

            if props.display_cameraBG_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.0
                icon = "VIEW_CAMERA" if item.hasBGImage() else "BLANK1"
                row.operator("uas_shot_manager.cambgitem", text="", icon=icon).index = index
                row.scale_x = 0.9

            if props.display_greasepencil_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.0
                icon = "OUTLINER_OB_GREASEPENCIL" if item.hasGreasePencil() else "BLANK1"
                row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index
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
        grid_flow = row.grid_flow(align=True, columns=3, even_columns=False)
        grid_flow.use_property_split = False
        grid_flow.scale_x = 2.6

        if props.display_camera_in_shotlist:
            if item.camera is None:
                grid_flow.alert = True
            grid_flow.prop(item, "camera", text="")
            grid_flow.scale_x = 0.3
            grid_flow.operator(
                "uas_shot_manager.list_camera_instances", text=str(props.getNumSharedCamera(item.camera))
            ).index = index
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
        row.operator("uas_shot_manager.unique_cameras", text="   Make All Cameras Unique")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shots_removecamera", text="   Remove Camera From All Shots...")

        #############
        # Act 01
        #############
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Act 01:")

        if config.uasDebug:
            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.operator("uasotio.openfilebrowser", text="   Create Shots From EDL").importMode = "CREATE_SHOTS"

        row = layout.row(align=True)
        #    row.operator_context = "INVOKE_DEFAULT"

        #############
        # Predec settings:
        argsDictPredecAct01 = dict()
        argsDictPredecAct01.update({"importStepMode": "PREDEC"})
        argsDictPredecAct01.update(
            {
                "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730.xml"
            }
        )
        argsDictPredecAct01.update({"animaticFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Act01_Predec.mp4"})
        argsDictPredecAct01.update({"conformMode": "CREATE"})
        # argsDictPredecAct01.update({"mediaHaveHandles": False})
        # argsDictPredecAct01.update({"mediaHandlesDuration": 0})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="   Create Shots From EDL - Predec Act 01"
        ).opArgs = json.JSONEncoder().encode(argsDictPredecAct01)

        row = layout.row(align=True)
        #    row.operator_context = "INVOKE_DEFAULT"

        #############
        # Previz settings:
        argsDictPrevAct01 = dict()
        argsDictPrevAct01.update({"importStepMode": "PREVIZ"})
        argsDictPrevAct01.update({"otioFile": r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml"})
        argsDictPrevAct01.update(
            {"animaticFile": r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4"}
        )
        argsDictPrevAct01.update({"conformMode": "UPDATE"})
        argsDictPrevAct01.update({"videoShotsFolder": r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Shots"})
        argsDictPrevAct01.update({"mediaInEDLHaveHandles": props.areShotHandlesUsed()})
        argsDictPrevAct01.update({"mediaInEDLHandlesDuration": props.getHandlesDuration()})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="   Update Shots From EDL - Previz Act 01"
        ).opArgs = json.JSONEncoder().encode(argsDictPrevAct01)

        #############
        # Debug Seq 60:
        if config.uasDebug:
            row = layout.row(align=True)
            argsDictDebugModifs = dict()
            argsDictDebugModifs.update({"importStepMode": "PREVIZ"})
            argsDictDebugModifs.update(
                {
                    #    "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_To40_RefDebug_SwapSeq30_20-30.xml"
                    "otioFile": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.xml"
                }
            )
            # argsDictDebugModifs.update(
            #     {
            #         "animaticFile": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PredecAct01\PredecAct01_To40.mp4"
            #     }
            # )
            argsDictDebugModifs.update({"conformMode": "UPDATE"})
            argsDictDebugModifs.update(
                {
                    "videoShotsFolder": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Shots"
                }
            )
            argsDictDebugModifs.update({"mediaInEDLHaveHandles": props.areShotHandlesUsed()})
            argsDictDebugModifs.update({"mediaInEDLHandlesDuration": props.getHandlesDuration()})
            # argsDictDebugModifs.update({"mediaHaveHandles": props.areShotHandlesUsed()})
            # argsDictDebugModifs.update({"mediaHandlesDuration": props.getHandlesDuration()})

            row.operator(
                "uasshotmanager.createshotsfromotio_rrs", text="   Update Shots From EDL - Debug Confo Seq0060"
            ).opArgs = json.JSONEncoder().encode(argsDictDebugModifs)
            # row.operator(
            #     "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug 40 swap"
            # ).otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_To40_RefDebug_SwapSeq30_20-30.xml"  # _to40

        #############
        # Act 02
        #############

        layout.separator()
        row = layout.row(align=True)
        row.label(text="Act 02:")
        row = layout.row(align=True)

        #    row.operator_context = "INVOKE_DEFAULT"

        # Predec settings:
        argsDictPredecAct02 = dict()
        argsDictPredecAct02.update({"importStepMode": "PREDEC"})
        argsDictPredecAct02.update(
            {
                "otioFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act02\Exports\RRSpecial_Act02_AQ_XML\RRspecial_Act02_AQ_201007.xml"
            }
        )
        argsDictPredecAct02.update({"animaticFile": r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act02\Act02_Predec.mp4"})
        argsDictPredecAct02.update({"conformMode": "CREATE"})
        # argsDictPredecAct02.update({"mediaHaveHandles": props.areShotHandlesUsed()})
        # argsDictPredecAct02.update({"mediaHandlesDuration": props.getHandlesDuration()})
        # argsDictPredecAct02.update({"mediaHaveHandles": False})
        # argsDictPredecAct02.update({"mediaHandlesDuration": 0})

        row.operator(
            "uasshotmanager.createshotsfromotio_rrs", text="   Create Shots From EDL - Predec Act 02"
        ).opArgs = json.JSONEncoder().encode(argsDictPredecAct02)

        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uasshotmanager.createshotsfromotio_rrs", text="   Create Shots From EDL - Debug")

        if config.uasDebug:
            row = layout.row(align=True)

            argsDictRefDebug = dict()
            argsDictRefDebug.update({"importStepMode": "PREDEC"})
            argsDictRefDebug.update(
                {
                    "otioFile": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PredecAct01\PredecAct01_To40.xml"
                }
            )
            argsDictRefDebug.update(
                {
                    "animaticFile": r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PredecAct01\PredecAct01_To40.mp4"
                }
            )
            argsDictRefDebug.update({"conformMode": "CREATE"})

            row.operator(
                "uasshotmanager.createshotsfromotio_rrs", text="   Create Shots From EDL - Debug 40"
            ).opArgs = json.JSONEncoder().encode(argsDictRefDebug)

        # tools for precut ###
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Tools for Precut:")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uas_shot_manager.predec_shots_from_single_cam", text="   Create Shots From Single Camera...")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.print_montage_info", text="   Print montage information in the console")

        # tools for precut ###
        layout.separator()
        row = layout.row(align=True)
        row.label(text="RRS Specific:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.predec_sort_versions_shots", text="   Sort Version Shots")


classes = (
    UAS_UL_ShotManager_Items,
    UAS_MT_ShotManager_Shots_ToolsMenu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

