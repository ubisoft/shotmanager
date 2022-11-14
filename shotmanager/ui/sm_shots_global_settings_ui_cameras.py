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
Grease pencil viewport overlay draw functions
"""

from shotmanager.config import config


def draw_camera_global_settings(context, layout, mode="SHOT"):
    """Used for storyboard frames and grease pencil shots in the Shot Manager storyboard panel,
    and by the 2.5D grease pencil panel
    Args:
        mode:   can be "STORYBOARD", "GP", "SHOT"
    """

    props = config.getAddonProps(context.scene)
    # prefs = config.getAddonPrefs()
    splitFactor = 0.16

    titleSplit = layout.split(factor=0.25)
    # titleSplit.label(text="Cameras: ")
    titleSplit.label(text="Passepartout:")
    titleRowRight = titleSplit.row(align=False)
    # titleRowRight.alignment = "RIGHT"

    #   layout.separator(factor=0.5)

    # box = layout.box()
    # row = box.row(align=False)

    # leftRow = row.row()
    #    leftRow.prop(spaceDataViewport.overlay, "show_overlays", icon="OVERLAY", text="")
    # leftRow.label(text=" ")

    # rightRow = row.row()
    camerasCol = titleRowRight.column()

    # camerasSplit = camerasCol.split(factor=splitFactor)
    # camerasLeftRow = camerasSplit.row()
    # camerasLeftRow.label(text=" ")

    # camerasLeftRow.label(text="Overlays: ")

    # if mode in ["GP"]:
    #     camerasRighRow = camerasSplit.row()
    #     camerasRighRow.operator("uas_shot_manager.overlays_toggleonionskin", depress=onionSkinIsActive)
    #     camerasRighRow.operator("uas_shot_manager.overlays_togglecanvas", depress=gridIsActive)

    #     row = camerasCol.row(align=False)
    #     camerasSplit = row.split(factor=splitFactor)
    #     camerasSplit.separator()
    #     camerasRighRow = camerasSplit.row()
    #     camerasRighRow.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
    #     subCamerasRighRow = camerasRighRow.row()
    #     subCamerasRighRow.enabled = spaceDataViewport.overlay.use_gpencil_fade_layers
    #     subCamerasRighRow.prop(prefs, "stb_overlay_layers_opacity", text="Fade Layers", slider=True)

    if mode in ["STORYBOARD", "SHOT"]:
        row = camerasCol.row(align=False)
        camerasRighRow = row.row()
        camerasRighRow.prop(props.shotsGlobalSettings, "stb_show_passepartout", text="", slider=True)
        subCamerasRighRow = camerasRighRow.row()
        subCamerasRighRow.enabled = props.shotsGlobalSettings.stb_show_passepartout
        subCamerasRighRow.prop(props.shotsGlobalSettings, "stb_passepartout_alpha", text="", slider=True)
