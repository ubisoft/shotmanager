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


def draw_greasepencil_overlay_tools(context, layout, mode="SHOT"):
    """Used for storyboard frames and grease pencil shots in the Shot Manager storyboard panel,
    and by the 2.5D grease pencil panel
    Args:
        mode:   can be "STORYBOARD", "GP", "SHOT"
    """

    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    splitFactor = 0.16

    spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    onionSkinIsActive = False
    gridIsActive = False
    if spaceDataViewport is not None:
        onionSkinIsActive = spaceDataViewport.overlay.use_gpencil_onion_skin
        gridIsActive = spaceDataViewport.overlay.use_gpencil_grid

    row = layout.row(align=False)

    leftRow = row.row()
    leftRow.prop(spaceDataViewport.overlay, "show_overlays", icon="OVERLAY", text="")

    rightRow = row.row()
    rightRow.enabled = spaceDataViewport.overlay.show_overlays
    overlayCol = rightRow.column()

    overlaySplit = overlayCol.split(factor=splitFactor)
    overlayLeftRow = overlaySplit.row()
    overlayLeftRow.label(text="Overlay: ")

    if mode in ["GP", "STORYBOARD"]:
        overlayRighRow = overlaySplit.row()
        overlayRighRow.operator("uas_shot_manager.greasepencil_toggleonionskin", depress=onionSkinIsActive)
        overlayRighRow.operator("uas_shot_manager.greasepencil_togglecanvas", depress=gridIsActive)

        row = overlayCol.row(align=False)
        overlaySplit = row.split(factor=splitFactor)
        overlaySplit.separator()
        overlayRighRow = overlaySplit.row()
        overlayRighRow.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
        # row.prop(spaceDataViewport.overlay, "gpencil_fade_layer")
        subOverlayRighRow = overlayRighRow.row()
        subOverlayRighRow.enabled = spaceDataViewport.overlay.use_gpencil_fade_layers
        subOverlayRighRow.prop(prefs, "stb_overlay_layers_opacity", text="Fade Layers", slider=True)

        row = overlayCol.row(align=False)
        overlaySplit = row.split(factor=splitFactor)
        overlaySplit.separator()

    if mode in ["STORYBOARD", "SHOT"]:
        overlayRighRow = overlaySplit.row()
        subOverlayRighRow = overlayRighRow.row()
        subOverlayRighRow.prop(props.shotsGlobalSettings, "stb_show_passepartout", text="", slider=True)
        subsubOverlayRighRow = subOverlayRighRow.row()
        subsubOverlayRighRow.enabled = props.shotsGlobalSettings.stb_show_passepartout
        subsubOverlayRighRow.prop(props.shotsGlobalSettings, "stb_passepartout_alpha", text="Passepartout", slider=True)
