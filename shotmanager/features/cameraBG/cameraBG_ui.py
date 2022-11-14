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
Camera BG UI
"""


from shotmanager.config import config


def draw_cameraBG_shot_properties(layout, context, shot):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    if shot is None:
        return

    propertiesModeStr = "Selected " if "SELECTED" == props.current_shot_properties_mode else "Current "

    cameraIsValid = shot.isCameraValid()
    if not cameraIsValid:
        box = layout.box()
        row = box.row()
        row.label(text=propertiesModeStr + "Shot Camera BG:")
        row.alert = True
        if shot.camera is None:
            row.label(text="*** Camera not defined ! ***")
        else:
            row.scale_x = 1.1
            row.label(text="*** Referenced camera not in scene ! ***")
        return

    shotHasCamBG = len(shot.camera.data.background_images) and shot.camera.data.background_images[0].clip is not None

    box = layout.box()
    box.use_property_decorate = False
    row = box.row()
    extendSubRow = row.row(align=False)
    subrowleft = extendSubRow.row()
    subrowleft.scale_x = 0.75
    subrowleft.label(text=propertiesModeStr + "Shot Camera BG:")

    # subrowleft.scale_x = 0.8
    # panelIcon = "TRIA_DOWN" if prefs.shot_cameraBG_expanded and shotHasCamBG else "TRIA_RIGHT"
    # extendSubRow.prop(prefs, "shot_cameraBG_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    # subRow = row.row(align=True)
    # subRow.label(text="Selected Shot Camera BG:")
    # subRow.scale_x = 0.6
    if not shotHasCamBG:
        # extendSubRow.enabled = False
        row.operator(
            "uas_shot_manager.openfilebrowser_for_cam_bg", text="", icon="ADD", emboss=True
        ).pathProp = "inputOverMediaPath"
        row.prop(props, "display_cameraBG_in_shotlist", text="")
    else:
        subRow = extendSubRow.row(align=True)
        # subRow.alignment = "LEFT"
        subRow.prop(shot.camera.data.background_images[0].clip, "filepath", text="")
        subRow.operator(
            "uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True
        ).shotIndex = props.getShotIndex(shot)

        subRow.separator()
        subRow.prop(props, "display_cameraBG_in_shotlist", text="")

        if True or prefs.shot_cameraBG_expanded:
            if len(shot.camera.data.background_images):
                row = box.row()
                #    row.enabled = False
                row.separator(factor=1.0)
                row.prop(shot, "bgImages_linkToShotStart")
                row.prop(shot, "bgImages_offset")

            if config.devDebug:
                if shot.isCameraValid() and len(shot.camera.data.background_images):
                    bgClip = shot.camera.data.background_images[0].clip
                    row = box.row()
                    row.separator(factor=1.0)
                    row.label(
                        text=f"BG Clip:  {bgClip.name},  start:  {bgClip.frame_start} fr.,  Sound track ind.: {shot.bgImages_sound_trackIndex}"
                    )

            if config.devDebug:
                row = box.row()
                bgSoundStr = "Sound Clip: "

                if "" == shot.bgSoundClipName:
                    bgSoundStr += "None"
                else:
                    bgSoundStr += shot.bgSoundClipName + " "
                    if shot.isSoundSequenceValid():
                        bgSoundStr += " (valid) "
                        soundSequence = shot.getSoundSequence()
                        bgSoundStr += soundSequence.name
                    else:
                        bgSoundStr += " (*** invalid ***) "

                row.label(text=bgSoundStr)


def draw_cameraBG_global_properties(layout, context):
    props = config.getAddonProps(context.scene)

    box = layout.box()
    row = box.row()
    row.label(text="Shots Global Control:")
    rightRow = row.row()
    rightRow.alignment = "RIGHT"
    rightRow.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

    # # Camera background images
    # ######################

    row = box.row()
    row.use_property_decorate = False
    row.separator()

    col = row.column()
    subRow = col.row()
    grid_flow = subRow.grid_flow(align=False, columns=4, even_columns=False)
    grid_flow.label(text="Camera BG Images:")
    grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
    grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
    grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
    c = row.column()
    c.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE")

    if config.devDebug:
        row = col.row()
        row.separator(factor=1.0)
        c = row.column()
        c.enabled = False
        c.prop(props.shotsGlobalSettings, "proxyRenderSize")

    row = col.row()
    c = row.column()
    grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
    grid_flow.label(text="Camera BG Sound:")
    grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn On").useBackgroundSound = True
    grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn Off").useBackgroundSound = False
    grid_flow.prop(props.shotsGlobalSettings, "backgroundVolume", text="Volume")
    c.separator(factor=0.5)  # prevents stange look when panel is narrow

    # c = row.column()
    # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
    # grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

    # grid_flow.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)
