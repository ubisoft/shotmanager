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
Shot Manager main panel UI
"""

import bpy
from bpy.types import Panel, Operator, EnumProperty

from shotmanager.config import config

# from shotmanager.viewport_3d.ogl_ui import UAS_ShotManager_sequenceTimeline

from shotmanager.utils import utils

from . import sm_shots_ui
from . import sm_takes_ui
from . import sm_shot_settings_ui
from .warnings_ui import drawWarnings

from shotmanager.features.greasepencil import greasepencil_ui as gp

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

######
# Shot Manager main panel #
######


class UAS_PT_ShotManager(Panel):
    #    bl_label = f"Shot Manager {'.'.join ( str ( v ) for v in bl_info[ 'version'] ) }"
    bl_label = " Shot Manager  V. " + utils.addonVersion("Shot Manager")[0]
    bl_idname = "UAS_PT_Shot_Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"

    @classmethod
    def poll(cls, context):
        # props = context.scene.UAS_shot_manager_props
        # hide the whole panel if used
        # return not props.dontRefreshUI()
        return True

    def draw_header(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # if context.window_manager.  warning on addons missing - to do:
        #     row.alert = True
        # else:
        #     row.alert = False

        icon = config.icons_col["Ubisoft_32"]
        icon = config.icons_col["ShotManager_32"]
        row.operator("uas_shot_manager.about", text="", icon_value=icon.icon_id)

        if props.use_project_settings:
            if "" == props.project_name:
                row.alert = True
                row.label(text="<No Project Name>")
                row.alert = False
            else:
                row.label(text=props.project_name)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        # row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"
        # row.separator(factor=2)

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        versionStr = utils.addonVersion("Video Tracks")
        subRow = row.row()
        subRow.enabled = versionStr is not None
        subRow.operator(
            "uas_shot_manager.go_to_video_tracks", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "SM_CheckSequence"

        row.separator(factor=0.5)
        icon = config.icons_col["General_Explorer_32"]
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=0.5)
        row.menu("UAS_MT_Shot_Manager_prefs_mainmenu", icon="PREFERENCES", text="")
        row.separator(factor=1.0)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        currentTake = props.getCurrentTake()
        currentTakeInd = props.getCurrentTakeIndex()

        shot = None
        if "SELECTED" == props.current_shot_properties_mode:
            shot = props.getSelectedShot()
        else:
            shot = props.getCurrentShot()

        enlargeButs = 1.15

        # addon warning message - for beta message display
        ###############
        # import addon_utils

        # addonWarning = [
        #     addon.bl_info.get("warning", "")
        #     for addon in addon_utils.modules()
        #     if addon.bl_info["name"] == "Shot Manager"
        # ]

        addonWarning = [""]
        if "" != addonWarning[0]:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")
            row.alert = False

        if config.devDebug:
            row = layout.row()
            row.label(text="Debug Mode:")
            subrow = row.row()
            # subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = True
            subrow.alert = config.devDebug
            subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = False

        if config.devDebug:
            row = layout.row()
            row.alignment = "CENTER"
            strDebug = " *** Debug Mode ***"
            # if props.useBGSounds:
            #     strDebug += "  BG Sounds Used"
            row.alert = True
            row.label(text=strDebug)
            row.prop(props, "useBGSounds")
            row.alert = False

        if not props.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_shot_manager.initialize")
            row.alert = False
            layout.separator()

        # scene warnings
        ################
        warningsList = props.getWarnings(scene)
        drawWarnings(context, layout, warningsList, panelType="MAIN")

        # play and timeline
        ################
        playEnabled = not utils.sceneContainsCameraBinding(scene)
        row = layout.row()
        row.scale_y = 1.3
        rowPlayButton = row.row()
        rowPlayButton.enabled = playEnabled
        rowPlayButton.prop(
            context.window_manager,
            "UAS_shot_manager_shots_play_mode",
            text="Shots Play Mode" if context.window_manager.UAS_shot_manager_shots_play_mode else "Standard Play Mode",
            toggle=True,
            icon="ANIM" if context.window_manager.UAS_shot_manager_shots_play_mode else "FORWARD",
        )

        toggleButRow = row.row(align=True)
        toggleButRow.operator_context = "INVOKE_DEFAULT"
        toggleButRow.scale_x = 1.1
        icon = config.icons_col["ShotManager_Tools_OverlayTools_32"]
        toggleButRow.operator(
            "uas_shot_manager.display_overlay_tools",
            text="",
            depress=context.window_manager.UAS_shot_manager_display_overlay_tools,
            icon_value=icon.icon_id,
        )
        ## replaced by operators ########
        # toggleButRow.prop(
        #     context.window_manager,
        #     "UAS_shot_manager_display_overlay_tools",
        #     text="",
        #     toggle=True,
        #     icon_value=icon.icon_id,
        # )
        # subSubRow = toggleButRow.row(align=True)
        # subSubRow.enabled = context.window_manager.UAS_shot_manager_display_overlay_tools
        # subSubRow.prop(
        #     context.window_manager,
        #     "UAS_shot_manager_toggle_shots_stack_interaction",
        #     text="",
        #     icon="ARROW_LEFTRIGHT",
        #     toggle=True,
        # )

        subSubRow = toggleButRow.row(align=True)
        subSubRow.enabled = context.window_manager.UAS_shot_manager_display_overlay_tools
        subSubRow.operator(
            "uas_shot_manager.toggle_shots_stack_interaction",
            text="",
            icon="ARROW_LEFTRIGHT",
            depress=context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction,
        )
        #  subSubRow = toggleButRow.row(align=True)
        toggleButRow.prop(
            context.window_manager, "UAS_shot_manager_use_best_perfs", text="", icon="INDIRECT_ONLY_ON", toggle=True,
        )

        # row.prop(scene, "use_audio", text="", icon="PLAY_SOUND")      # works inverted :S
        toggleSoundRow = row.row(align=True)
        toggleSoundRow.scale_x = 1.1
        toggleSoundRow.operator("uas_shot_manager.use_audio", text="", icon="PLAY_SOUND", depress=not scene.use_audio)

        # play bar
        ################
        row = layout.row(align=True)

        row.enabled = playEnabled
        split = row.split(align=True)
        split.separator()
        row.alignment = "CENTER"
        subrow = row.row(align=True)
        subrow.enabled = 0 < len(props.get_shots())
        subrow.operator("uas_shot_manager.playbar_gotofirstshot", text="", icon="REW")
        icon = config.icons_col["ShotManager_Play_GoToPrevEnd_32"]
        subrow.operator("uas_shot_manager.playbar_gotopreviousshotboundary", text="", icon_value=icon.icon_id)
        subrow.operator("uas_shot_manager.playbar_gotopreviousframe", text="", icon="FRAME_PREV")

        split = row.split(align=True)
        split.separator()
        # row.ui_units_x = 40
        row.scale_x = 1.8
        row.operator(
            "SCREEN_OT_animation_play", text="", icon="PLAY" if not context.screen.is_animation_playing else "PAUSE"
        )
        row.scale_x = 1
        # if display_prev_next_buttons
        #  row.operator ( "SCREEN_OT_frame_jump", text = "", icon = "PLAY" if not context.screen.is_animation_playing else "PAUSE" )
        #     row.prop(context.scene, "frame_current", text = "")            # prend la propriété direct ds la scene

        split = row.split(align=True)
        split.separator()
        subrow = row.row(align=True)
        subrow.enabled = 0 < len(props.get_shots())
        subrow.operator("uas_shot_manager.playbar_gotonextframe", text="", icon="FRAME_NEXT")
        icon = config.icons_col["ShotManager_Play_GoToNextStart_32"]
        subrow.operator("uas_shot_manager.playbar_gotonextshotboundary", text="", icon_value=icon.icon_id)
        subrow.operator("uas_shot_manager.playbar_gotolastshot", text="", icon="FF")

        # separated frame spinner
        row.separator(factor=2.0)
        split = row.split(align=True)
        split.separator()
        row.prop(scene, "frame_current", text="")
        split = row.split(align=True)
        row.separator(factor=3.0)
        # split.separator ( )
        # wkip mettre une propriété
        # row.prop(scene.render, "fps_base", text="")
        if props.playSpeedGlobal != 100:
            row.alert = True
        row.prop(props, "playSpeedGlobal", text="")
        row.alert = False

        layout.separator(factor=0.5)

        ################
        # stop draw here if perfs are required
        ################
        if props.dontRefreshUI():
            return None

        # grease pencil
        ################

        if props.display_greasepencil_in_properties:  # and props.expand_greasepencil_properties:
            gp.draw_greasepencil_play_tools(layout, context, shot, layersListDropdown=prefs.layersListDropdown)

        # sequence name
        ################
        seqrow = layout.row()
        seqcol = seqrow.column(align=True)

        # if False:
        #     spacerrow = seqcol.row()
        #     spacerrow.scale_y = 0.3
        #     spacerrow.alignment = "CENTER"
        #     spacerrow.label(text="           -------------------------------------------------------")
        #     # spacerrow.scale_y = 1.0

        seqcol.separator(factor=0.8)
        namerow = seqcol.row(align=True)
        namerow.scale_y = 1.2
        leftrow = namerow.row()
        leftrow.alignment = "LEFT"
        leftrow.label(text="Sequence:")

        rightsplit = namerow.split(align=True, factor=0.7)
        # subnamerow.scale
        #  rightsplit.alignment = "RIGHT"
        rightsplitrow = rightsplit.row(align=True)
        rightsplitrow.prop(props, "sequence_name", text="")
        subnamerow = rightsplit.row(align=True)
        subnamerow.separator(factor=0.2)
        # subnamerow.operator(
        #     "shot_manager.workspace_info",
        #     text="",
        #     icon="WORDWRAP_ON",
        #     depress=context.window_manager.UAS_shot_manager_identify_3dViews,
        #     emboss=False,
        # )

        # subnamerow.alignment = "RIGHT"
        activeindrow = subnamerow.row(align=True)
        # activeindrow.scale_x = 0.4
        subactiveindrow = activeindrow.row(align=True)
        subactiveindrow.prop(
            context.window_manager, "UAS_shot_manager_identify_3dViews", text="", toggle=True, icon="WORDWRAP_ON",
        )
        targviewprow = subactiveindrow.row(align=True)
        expected_target_area_ind = props.getTargetViewportIndex(context, only_valid=False)
        target_area_ind = props.getTargetViewportIndex(context, only_valid=True)
        # print(f"display area targ: expected_target_area_ind:{expected_target_area_ind}, targ:{target_area_ind}")
        targviewprow.alert = target_area_ind < expected_target_area_ind
        targviewprow.prop(props, "target_viewport_index", text="")

        # target_area = props.getValidTargetViewport(context)

        #  subnamerow.prop(context.window_manager, "shotmanager_target_viewport", text="")

        subnamerow = namerow
        subnamerow.separator(factor=1.7)
        subnamerow.operator("shot_manager.features", text="", icon="PROPERTIES", emboss=False)
        subnamerow.separator(factor=0.5)
        seqcol.separator(factor=0.3)
        # seqcol.label(text="________________________")

        # editing
        ################
        if props.display_editmode_in_properties:
            box = layout.box()
            editrow = box.row()
            leftrow = editrow.row()
            leftrow.alignment = "LEFT"
            # leftrow.scale_x = 0.8
            leftrow.label(text="Edit:")

            rightrow = editrow.row()
            editingDuration = props.getEditDuration()
            editingDurationStr = "-" if -1 == editingDuration else (str(editingDuration) + " fr.")
            rightrow.label(text="Duration: " + editingDurationStr)

            # editrow.separator()
            #    editrow = layout.row(align=True)
            # context.props.getCurrentShotIndex(ignoreDisabled = False
            editingCurrentTime = props.getEditCurrentTime()
            editingCurrentTimeStr = "-" if -1 == editingCurrentTime else str(editingCurrentTime)
            rightrow.label(text="Current Time in Edit: " + editingCurrentTimeStr)

            rightrow.alignment = "RIGHT"

            if props.use_project_settings and props.project_fps != scene.render.fps:
                rightrow.alert = True
            rightrow.label(text=str(scene.render.fps) + " fps")

        # takes
        ################
        panelIcon = "TRIA_DOWN" if prefs.take_properties_expanded else "TRIA_RIGHT"
        takeHasNotes = False
        if currentTake is not None:
            takeHasNotes = currentTake.hasNotes()

        box = layout.box()
        row = box.row(align=False)

        # if props.display_globaleditintegr_in_properties or props.display_notes_in_properties or props.display_takerendersettings_in_properties or takeHasNotes:
        display_take_arrow = (
            props.display_globaleditintegr_in_properties or props.display_takerendersettings_in_properties
        )
        if display_take_arrow:
            # utils_ui.collapsable_panel(row, prefs, "take_properties_expanded")     # doesn't improve the UI
            row.prop(prefs, "take_properties_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

        leftrow = row.row()
        leftrow.alignment = "LEFT"
        leftrow.scale_x = 0.81 if display_take_arrow else 1.16
        takeStr = "Take:" if not props.display_advanced_infos else f"Take ({currentTakeInd + 1}/{props.getNumTakes()}):"
        leftrow.label(text=takeStr)

        subrow = row.row(align=True)
        #    row.scale_y = 1.5
        subrow.scale_x = 2.0

        subsubrow = subrow.row(align=True)
        subsubrow.scale_x = 0.8
        # subsubrow.use_property_split = True

        if currentTake is not None:

            # reduce space between buttons:
            # if currentTake.overrideRenderSettings or takeHasNotes or props.display_notes_in_properties:

            if currentTake.overrideRenderSettings:
                # overrideRow = subsubrow.row()
                # overrideRow.alert = True
                # overrideRow.scale_x = 0.4
                # overrideRow.label(text="Ov.")

                # overrideRow.alert = True
                overIcon = "DECORATE_OVERRIDE"
                subsubrow.prop(
                    prefs,
                    "take_renderSettings_expanded",
                    text="",
                    emboss=prefs.take_renderSettings_expanded,
                    # emboss=True,
                    icon=overIcon,
                )

            if takeHasNotes:
                icon = config.icons_col["ShotManager_NotesData_32"]
                subsubrow.prop(
                    prefs, "take_notes_expanded", text="", emboss=prefs.take_notes_expanded, icon_value=icon.icon_id
                )
            else:
                if props.display_notes_in_properties:
                    icon = config.icons_col["ShotManager_NotesNoData_32"]
                    subsubrow.prop(
                        prefs, "take_notes_expanded", text="", emboss=prefs.take_notes_expanded, icon_value=icon.icon_id
                    )
                    # emptyIcon = config.icons_col["General_Empty_32"]
                    # row.operator(
                    #     "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
                    # ).index = index

        subrow.prop(props, "current_take_name", text="")
        #    row.menu(UAS_MT_ShotManager_Takes_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')

        timerow = row.row(align=True)
        timerow.alignment = "RIGHT"
        timerow.scale_x = enlargeButs
        timerow.operator("uas_shot_manager.scenerangefromtake", text="", icon="PREVIEW_RANGE")

        # row = row.row(align=False)
        row.menu("UAS_MT_Shot_Manager_takes_toolsmenu", icon="TOOL_SETTINGS", text="")

        if prefs.take_properties_expanded:
            #  row = box.row()
            #  row.label(text="Take Properties:")

            # Global edit
            ######################
            if props.display_globaleditintegr_in_properties:
                subBox = box.box()
                subRow = subBox.row()
                subRow.separator()
                subRow.prop(currentTake, "globalEditDirectory", text="Edit Dir")
                subRow = subBox.row()
                subRow.separator()
                subRow.prop(currentTake, "globalEditVideo", text="Edit Animatic")
                subRow = subBox.row()
                subRow.separator()
                subRow.prop(currentTake, "startInGlobalEdit", text="Start in Global Edit")

            if props.display_globaleditintegr_in_properties:
                box.separator(factor=0.2)

        # Render settings properties
        ######################
        # if props.display_takerendersettings_in_properties:
        if currentTake is not None and (
            (props.display_takerendersettings_in_properties and prefs.take_properties_expanded)
            or (props.display_takerendersettings_in_properties and prefs.take_renderSettings_expanded)
            or (currentTake.overrideRenderSettings and prefs.take_renderSettings_expanded)
            # or (takeHasNotes and prefs.take_properties_expanded)
        ):
            panelIcon = "TRIA_DOWN" if prefs.take_renderSettings_expanded else "TRIA_RIGHT"

            subBox = box.box()
            subBox.use_property_decorate = False
            titleRow = subBox.row()
            titleRow.prop(prefs, "take_renderSettings_expanded", text="", icon=panelIcon, emboss=False)
            titleRow.label(text="Take Render Settings:")

            # overSubRow = subRow.split(factor=0.05)
            overSubRow = titleRow.row(align=True)
            if currentTake.overrideRenderSettings:
                overSubRow.alert = True
            overSubRow.prop(currentTake, "overrideRenderSettings", text="")
            overSubRow.label(
                text="Override " + ("Project" if props.use_project_settings else "Scene") + " Render Settings"
            )

            if prefs.take_renderSettings_expanded:
                subSubBoxRow = subBox.row()
                subSubBoxRow.separator(factor=1)
                subSubBox = subSubBoxRow.column()
                # subSubBox.separator(factor=2)
                currentTake.outputParams_Resolution.draw(context, subSubBox, enabled=currentTake.overrideRenderSettings)

        # Notes
        ######################
        if currentTake is not None and (
            (props.display_notes_in_properties and prefs.take_properties_expanded)
            or (props.display_notes_in_properties and prefs.take_notes_expanded)
            or (takeHasNotes and prefs.take_notes_expanded)
            # or (takeHasNotes and prefs.take_properties_expanded)
        ):
            # or (props.display_notes_in_properties and prefs.take_properties_expanded)
            # ):
            panelIcon = "TRIA_DOWN" if prefs.take_notes_expanded else "TRIA_RIGHT"

            subBox = box.box()
            subBox.use_property_decorate = False
            titleRow = subBox.row()
            titleRow.prop(prefs, "take_notes_expanded", text="", icon=panelIcon, emboss=False)
            # row.separator(factor=1.0)
            c = titleRow.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            subrow = c.row()
            subrow.label(text="Take Notes:")
            subrow.separator(factor=0.5)  # prevents strange look when panel is narrow

            if prefs.take_notes_expanded:
                row = subBox.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note01", text="")
                row.separator(factor=1.0)
                row = subBox.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note02", text="")
                row.separator(factor=1.0)
                row = subBox.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note03", text="")
                row.separator(factor=1.0)
                box.separator(factor=0.1)

        # shots
        ################
        if len(props.takes):
            # numShots = len(props.getShotsList(ignoreDisabled=False))
            # numEnabledShots = len(props.getShotsList(ignoreDisabled=True))
            numShots = props.getNumShots()
            numEnabledShots = props.getNumShots(ignoreDisabled=True)
            display_adv_features = props.display_greasepencil_in_properties or props.display_cameraBG_in_properties

            box = layout.box()
            shotsrow = box.row()

            # leftmainsplit = shotsrow.split(factor=0.3, align=False)

            # column_flow = row.column_flow(columns=3)
            # subrow = column_flow.row()
            # subrow.alignment = "LEFT"
            # subrow.scale_x = 1.0

            shotsrowleft = shotsrow.row(align=True)
            # shotsrowleft.alignment = "LEFT"
            shotsrowlefttxt = shotsrowleft.row(align=True)
            shotsrowlefttxt.alignment = "LEFT"

            shotsStr = "Shots:" if not props.display_advanced_infos else f"Shots ({numEnabledShots}/{numShots}):"
            shotsrowlefttxt.label(text=shotsStr)
            #   shotsrowlefttxt.operator("uas_shot_manager.enabledisableall", text="", icon="TIME")

            # subrow.separator()
            #  column_flow.scale_x = 1.0
            # subrow = column_flow.row()
            # subrow.alignment = "LEFT"
            #   subrow.scale_x = 1.0

            # rightmainsplit = shotsrow.split()
            # rightmainsplit.alert = True

            #  shotsrowright = shotsrow.row(align=True)

            # spacer
            spacerrow = shotsrowleft.row(align=False)
            spacerrow.alignment = "LEFT"
            spacerrow.scale_x = 1.26 if props.display_notes_in_properties else 0.92
            spacerrow.label(text="")
            # spacerrow.separator(factor=1)

            # edit ############
            ###########################
            #  shotsrow.alignment = "EXPAND"

            subrowedit = shotsrowleft.row(align=False)
            subrowedit.alignment = "RIGHT"
            iconCheckBoxes = "CHECKBOX_HLT" if not prefs.toggleShotsEnabledState else "CHECKBOX_DEHLT"
            subrowedit.operator("uas_shot_manager.enabledisableall", text="", icon=iconCheckBoxes, emboss=False)

            if props.display_editmode_in_properties:
                subrowedit.prop(
                    props,
                    "display_edit_times_in_shotlist",
                    text="" if False and display_adv_features else "Edit Times",
                    toggle=True,
                    icon="SEQ_STRIP_DUPLICATE",
                )

            if True or not display_adv_features:
                spacerrow = shotsrowleft.row(align=False)
                spacerrow.alignment = "EXPAND"
                #   spacerrow.scale_x = 0.5
                spacerrow.label(text="")
                # spacerrow.separator(factor=1)

            # tools ############
            ###########################

            # !!! keep align at False to preserve constant size for right buttons
            shotsrowright = shotsrow.row(align=False)
            shotsrowright.alignment = "RIGHT"

            shotsrow = shotsrowright

            if display_adv_features:
                subrowtools = shotsrow.row(align=True)
                #    subrowtools.separator(factor=0.5)
                # subrow.scale_x = 0.9
                subrowtools.alignment = "LEFT"
                # subrowtools.scale_x = 0.9

                if props.display_greasepencil_in_properties:
                    icon = (
                        config.icons_col["ShotManager_CamGPVisible_32"]
                        if not prefs.toggleGreasePencil
                        else config.icons_col["ShotManager_CamGPHidden_32"]
                    )
                    subrowtools.operator(
                        "uas_shot_manager.enabledisablegreasepencil", text="", icon_value=icon.icon_id, emboss=False
                    )

                if props.display_cameraBG_in_properties:
                    icon = (
                        config.icons_col["ShotManager_CamBGVisible_32"]
                        # config.icons_col["ShotManager_Image_32"]
                        if not prefs.toggleCamsBG
                        else config.icons_col["ShotManager_CamBGHidden_32"]
                    )
                    subrowtools.operator(
                        "uas_shot_manager.enabledisablecamsbg", text="", icon_value=icon.icon_id, emboss=False
                    )

                    icon = (
                        config.icons_col["ShotManager_CamSoundVisible_32"]
                        # config.icons_col["ShotManager_Image_32"]
                        if not prefs.toggleCamsSoundBG
                        else config.icons_col["ShotManager_CamSoundHidden_32"]
                    )
                    subrowtools.operator(
                        "uas_shot_manager.enabledisablesoundbg", text="", icon_value=icon.icon_id, emboss=False
                    )

            # camera tools ############
            ###########################

            #  subrow.scale_x = 1.0
            camrow = shotsrow.row(align=True)
            camrow.alignment = "RIGHT"
            camrow.scale_x = enlargeButs

            icon = config.icons_col["ShotManager_Tools_CamToView_32"]
            camrow.operator_context = "INVOKE_DEFAULT"
            camrow.operator("uas_utils.camera_to_view", text="", icon_value=icon.icon_id)  # icon="TRANSFORM_ORIGINS"

            camrow.alert = props.useLockCameraView
            camrow.prop(props, "useLockCameraView", text="", icon="CAMERA_DATA")
            camrow.alert = False

            # time tools ############
            ###########################

            timerow = shotsrow.row(align=True)
            timerow.alignment = "RIGHT"
            timerow.scale_x = enlargeButs
            timerow.operator("uas_shot_manager.scenerangefromshot", text="", icon="PREVIEW_RANGE")

            # col = row.column(align=True)
            # shotsrow.separator(factor=3.2)
            # row.operator("uas_shot_manager.shots_prefs", text="", icon="SETTINGS")
            #  shotsrow.operator("shot_manager.features", text="", icon="PROPERTIES")
            shotsrow.menu("UAS_MT_Shot_Manager_shots_toolsmenu", icon="TOOL_SETTINGS", text="")

            ##################################################
            ##################################################

            row = box.row()
            row.template_list(
                "UAS_UL_ShotManager_Items", "", currentTake, "shots", props, "selected_shot_index", rows=6
            )

            col = row.column(align=True)
            col.operator("uas_shot_manager.shot_add", icon="ADD", text="")
            col.operator("uas_shot_manager.shot_duplicate", icon="DUPLICATE", text="")
            col.operator("uas_shot_manager.shot_remove", icon="REMOVE", text="")
            col.separator()
            col.operator("uas_shot_manager.shot_move", icon="TRIA_UP", text="").action = "UP"
            col.operator("uas_shot_manager.shot_move", icon="TRIA_DOWN", text="").action = "DOWN"
            col.separator()
            #   col.menu("UAS_MT_Shot_Manager_shots_toolsmenu", icon="TOOL_SETTINGS", text="")

            row = layout.row()

        if 0 < numShots:
            if shot is not None:
                sm_shot_settings_ui.drawShotPropertiesToolbar(layout, context, shot)

        # layout.separator ( factor = 1 )


#########
# MISC
#########


class UAS_PT_ShotManager_Initialize(Operator):
    bl_idname = "uas_shot_manager.initialize"
    bl_label = "Initialize Shot Manager"
    bl_description = "Initialize Shot Manager"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.UAS_shot_manager_props.initialize_shot_manager()

        return {"FINISHED"}


classes = (
    UAS_PT_ShotManager,
    #  UAS_ShotManager_sequenceTimeline,
    UAS_PT_ShotManager_Initialize,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    sm_takes_ui.register()
    sm_shots_ui.register()
    sm_shot_settings_ui.register()


def unregister():
    sm_shot_settings_ui.unregister()
    sm_shots_ui.unregister()
    sm_takes_ui.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
