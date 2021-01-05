import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from shotmanager.utils import utils
from shotmanager.config import config


def draw_cameraBG_shot_properties(sm_ui, context, shot):
    layout = sm_ui.layout
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    scene = context.scene

    shotHasCamBG = len(shot.camera.data.background_images) and shot.camera.data.background_images[0].clip is not None
    panelIcon = "TRIA_DOWN" if prefs.shot_cameraBG_extended and shotHasCamBG else "TRIA_RIGHT"

    box = layout.box()
    box.use_property_decorate = False
    row = box.row()
    extendSubRow = row.row(align=True)
    extendSubRow.prop(prefs, "shot_cameraBG_extended", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    subRow = row.row(align=True)
    subRow.scale_x = 0.6
    subRow.label(text="Camera BG:")
    if not shotHasCamBG:
        extendSubRow.enabled = False
        row.operator(
            "uas_shot_manager.openfilebrowser_for_cam_bg", text="", icon="ADD", emboss=True
        ).pathProp = "inputOverMediaPath"
        row.prop(props, "display_cameraBG_in_shotlist", text="")
    else:
        subRow = row.row(align=True)
        subRow.prop(shot.camera.data.background_images[0].clip, "filepath", text="")
        subRow.operator(
            "uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True
        ).shotIndex = props.getShotIndex(shot)

        subRow.separator()
        subRow.prop(props, "display_cameraBG_in_shotlist", text="")

        if prefs.shot_cameraBG_extended:
            if len(shot.camera.data.background_images):
                row = box.row()
                #    row.enabled = False
                row.separator(factor=1.0)
                row.prop(shot, "bgImages_linkToShotStart")
                row.prop(shot, "bgImages_offset")

            if config.uasDebug:
                if shot.camera is not None and len(shot.camera.data.background_images):
                    bgClip = shot.camera.data.background_images[0].clip
                    row = box.row()
                    row.separator(factor=1.0)
                    row.label(
                        text=f"BG Clip:  {bgClip.name},  start:  {bgClip.frame_start} fr.,  Sound track ind.: {shot.bgImages_sound_trackIndex}"
                    )

            if config.uasDebug:
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
