import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty

from shotmanager.config import config
from shotmanager.utils import utils

from shotmanager.features.cameraBG import cameraBG_ui as cBG
from shotmanager.features.soundBG import soundBG_ui as sBG
from shotmanager.features.greasepencil import greasepencil_ui as gp

import logging

_logger = logging.getLogger(__name__)


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
            shot = props.getShotByIndex(props.selected_shot_index)
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
        layout = self.layout
        props = scene.UAS_shot_manager_props
        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid

        if itemHasWarnings:
            row = layout.row()
            layout.alignment = "RIGHT"
            row.alignment = "RIGHT"
            row.alert = True
            row.label(text="*** Warning: Camera not in scene !***")

        if config.uasDebug and props.display_greasepencil_in_properties:
            shot = None
            if not ("SELECTED" == props.current_shot_properties_mode):
                shot = props.getCurrentShot()
            else:
                shot = props.getShotByIndex(props.selected_shot_index)

            if shot is not None:
                if shot.camera is None:
                    row = layout.row()
                    row.enabled = False
                    row.operator("uas_shot_manager.add_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL")
                else:
                    gp_child = utils.get_greasepencil_child(shot.camera)
                    if gp_child is not None:
                        layout.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="GP_SELECT_STROKES")

                    # else:
                    #     layout.operator(
                    #         "uas_shot_manager.add_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL"
                    #     ).cameraGpName = shot.camera.name

        layout.operator(
            "uas_shot_manager.go_to_video_shot_manager", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "RRS_CheckSequence"

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons["shotmanager"].preferences
        props = scene.UAS_shot_manager_props
        iconExplorer = config.icons_col["General_Explorer_32"]

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)

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

            ####################
            # name and color
            row = box.row()
            row.separator(factor=0.5)
            grid_flow = row.grid_flow(align=False, columns=4, even_columns=False)
            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=False)

            subRowCam.prop(shot, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            # rowCam = grid_flow.row(align=False)
            subSubRow = subRowCam.row(align=True)
            subColor = subSubRow.row()
            subColor.scale_x = 0.2
            subColor.prop(shot, "color", text="")
            #   grid_flow.scale_x = 1.0
            subSubRow.separator(factor=1.0)
            subSubRow.prop(props, "display_color_in_shotlist", text="")
            subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

            ####################
            # Duration
            row = box.row()
            row.separator(factor=0.5)
            grid_flow = row.grid_flow(align=True, columns=4, even_columns=False)
            # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )

            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)

            subRowCam.label(text="Duration: ")

            subRowCam.use_property_split = False
            subRowCam.prop(
                shot,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if shot.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            subRowCam.prop(shot, "duration_fp", text="")

            #    grid_flow.label(text=str(shot.getDuration()) + " frames")
            subRowCam.separator(factor=1.0)
            subRowCam.prop(props, "display_duration_in_shotlist", text="")
            subRowCam.separator(factor=0.5)  # prevents stange look when panel is narrow

            ####################
            # camera and lens
            cameraIsValid = shot.isCameraValid()

            row = box.row()
            row.separator(factor=0.5)
            grid_flow = row.grid_flow(align=False, columns=4, even_columns=False)

            if not cameraIsValid:
                grid_flow.alert = True

            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)
            subRowCam.scale_x = 1.2

            grid_flow = subRowCam.grid_flow(align=True, columns=4, even_columns=False)
            # subSubRowCam = subRowCam.row(align=True)
            grid_flow.scale_x = 0.2
            grid_flow.label(text="Camera:")
            grid_flow.scale_x = 1.8
            grid_flow.prop(shot, "camera", text="")
            grid_flow.scale_x = 0.4
            grid_flow.operator(
                "uas_shot_manager.list_camera_instances", text=str(props.getNumSharedCamera(shot.camera))
            ).index = props.selected_shot_index

            if not cameraIsValid:
                grid_flow.alert = True
            subRowCam.separator(factor=1)
            subRowCam.prop(props, "display_camera_in_shotlist", text="")

            subRowCam = rowCam.row(align=True)
            # c.separator( factor = 0.5 )   # prevents strange look when panel is narrow
            subRowCam.scale_x = 1
            #     row.label ( text = "Lens: " )
            subRowCam.use_property_decorate = True
            subSubRowCam = subRowCam.row(align=False)
            subSubRowCam.scale_x = 0.5
            if not cameraIsValid:
                subSubRowCam.alert = True
                subSubRowCam.operator("uas_shot_manager.nolens", text="No Lens")
                subSubRowCam.alert = False
            else:
                subSubRowCam.prop(shot.camera.data, "lens", text="Lens")
            # subRowCam.scale_x = 1.0
            subRowCam.separator(factor=1)  # prevents strange look when panel is narrow
            subRowCam.prop(props, "display_lens_in_shotlist", text="")
            subRowCam.separator(factor=0.5)  # prevents strange look when panel is narrow
            # row.separator(factor=0.5)  # prevents strange look when panel is narrow

            box.separator(factor=0.5)

            ####################
            # Output
            row = box.row()
            row.separator(factor=1.0)
            grid_flow = row.grid_flow(align=False, columns=3, even_columns=False)
            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)

            subRowCam.label(text="Output: ")
            subRowCam.label(
                text="<Render Root Path> \\ "
                + shot.getParentTake().getName_PathCompliant()
                + " \\ "
                + shot.getOutputMediaPath(providePath=False)
            )
            subRowCam.operator(
                "uas_shot_manager.open_explorer", emboss=True, icon_value=iconExplorer.icon_id, text=""
            ).path = shot.getOutputMediaPath()
            subRowCam.separator(factor=0.5)  # prevents strange look when panel is narrow

            # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

            ######################
            # Notes
            ######################
            if props.display_notes_in_properties:
                panelIcon = "TRIA_DOWN" if prefs.shot_notes_extended else "TRIA_RIGHT"

                box = layout.box()
                box.use_property_decorate = False
                row = box.row()
                row.prop(prefs, "shot_notes_extended", text="", icon=panelIcon, emboss=False)
                # row.separator(factor=1.0)
                c = row.column()
                # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
                subrow = c.row()
                subrow.label(text="Shot Notes:")
                subrow.prop(props, "display_notes_in_shotlist", text="")
                #    subrow.separator(factor=0.5)

                if prefs.shot_notes_extended:
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

            ######################
            # Camera background images
            ######################
            if props.display_camerabgtools_in_properties and shot.camera is not None:
                cBG.draw_cameraBG_shot_properties(self, context, shot)

            ######################
            # Grease pencil
            ######################
            if props.display_greasepencil_in_properties and shot.camera is not None:
                gp.draw_greasepencil_shot_properties(self, context, shot)


classes = (UAS_PT_ShotManager_ShotProperties,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

