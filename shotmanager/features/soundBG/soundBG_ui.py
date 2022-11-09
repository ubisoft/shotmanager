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
Sounds bg ui
"""


from shotmanager.config import config


def draw_soundBG_shot_properties(sm_ui, context, shot):
    layout = sm_ui.layout
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()
    scene = context.scene

    shotHasCamBG = len(shot.camera.data.background_images) and shot.camera.data.background_images[0].clip is not None
    panelIcon = "TRIA_DOWN" if prefs.shot_cameraBG_expanded and shotHasCamBG else "TRIA_RIGHT"

    box = layout.box()
    box.use_property_decorate = False
    row = box.row()
    extendSubRow = row.row(align=True)
    extendSubRow.prop(prefs, "shot_cameraBG_expanded", text="", icon=panelIcon, emboss=False)
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

        if prefs.shot_cameraBG_expanded:
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
